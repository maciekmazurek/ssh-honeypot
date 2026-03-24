# SSH Honeypot

Lightweight SSH honeypot written in Python, designed to collect and analyze brute-force login attempts in a controlled environment.

## Key Features

- Fake SSH server listening on configurable port (default: 2222)
- Always denies authentication (safe honeypot behavior)
- Captures login attempts to JSON Lines format (`logs/attempts.jsonl`)
- Enriches attempts with geolocation metadata (country, city, ISP, ASN)
- Dockerized deployment (`Dockerfile`, `docker-compose.yml`)

## Quick Start

### Option 1: Docker Compose (recommended)

```bash
docker compose up -d --build
docker compose logs -f honeypot
```

Stop:

```bash
docker compose down
```

### Option 2: Local Python Run

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ssh-keygen -t rsa -b 2048 -f server.key -N ""
python honeypot.py
```

## Example Captured Record

```json
{
	"timestamp": "2026-03-24T18:12:06.532901+00:00",
	"ip": "203.0.113.10",
	"username": "root",
	"password": "admin123",
	"country": "Germany",
	"country_code": "DE",
	"city": "Frankfurt",
	"isp": "Example ISP",
	"asn": "AS12345"
}
```

## Security Notes

- Use only in lab/test environments or on infrastructure you own/manage.
- Never expose this publicly without legal authorization and monitoring.

## Current Hardening Choices

- Non-root user inside container
- Read-only root filesystem in Compose
- `no-new-privileges` container option
- Dedicated writable mount for logs
- Temporary filesystem mounted at `/tmp`

## Tech Stack

- Python 3.12
- Paramiko
- Requests
- Docker + Docker Compose
