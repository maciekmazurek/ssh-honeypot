import socket
import threading
import paramiko
import json
import logging
import os
from pathlib import Path
from datetime import datetime, UTC
from geo import get_geo

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=str(LOGS_DIR / "attempts.log"), level=logging.INFO)

HOST_KEY = paramiko.RSAKey(filename="server.key")

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        geo = get_geo(self.client_ip)

        entry = {
            "timestamp":    datetime.now(UTC).isoformat(),
            "ip":           self.client_ip,
            "username":     username,
            "password":     password,
            "country":      geo.get("country"),
            "country_code": geo.get("country_code"),
            "city":         geo.get("city"),
            "isp":          geo.get("isp"),
            "asn":          geo.get("asn"),
        }
        with open(LOGS_DIR / "attempts.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return paramiko.AUTH_FAILED

def handle_connection(client_socket, client_addr):
    client_ip = client_addr[0]
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)
    server = FakeSSHServer(client_ip)
    try:
        transport.start_server(server=server)
        transport.join(timeout=10)
    except Exception:
        pass
    finally:
        transport.close()

def run_honeypot(port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    sock.listen(100)
    sock.settimeout(1.0)
    print(f"[*] Honeypot listening on port {port}")
    try:
        while True:
            try:
                client, addr = sock.accept()
            except socket.timeout:
                continue

            t = threading.Thread(target=handle_connection, args=(client, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Ctrl+C received, shutting down honeypot.")
    finally:
        sock.close()

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    port = int(os.getenv("HONEYPOT_PORT", 2222))
    run_honeypot(port)