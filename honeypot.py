import socket
import threading
import paramiko
import json
import logging
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=str(LOGS_DIR / "attempts.log"), level=logging.INFO)

HOST_KEY = paramiko.RSAKey(filename="server.key")

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": self.client_ip,
            "username": username,
            "password": password,
        }
        with open(LOGS_DIR / "attempts.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logging.info(f"LOGIN ATTEMPT: {entry}")
        return paramiko.AUTH_FAILED  # Always fail

    def get_allowed_auths(self, username):
        return "password"

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
    print(f"[*] Honeypot listening on port {port}")
    while True:
        client, addr = sock.accept()
        t = threading.Thread(target=handle_connection, args=(client, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    run_honeypot()