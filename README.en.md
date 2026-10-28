# Zabbix MCP Server Universal

[![CI - Continuous Integration](https://github.com/seu-usuario/zabbix-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/seu-usuario/zabbix-mcp-server/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0%2B%20%2F%202.x-green)](https://modelcontextprotocol.io/)
[![Zabbix](https://img.shields.io/badge/Zabbix-6.0%20%7C%206.4%20%7C%207.0%20LTS%20%7C%207.4-red)](https://www.zabbix.com/)

Production-grade **Model Context Protocol (MCP)** server for **Zabbix Enterprise Monitoring**, featuring **100 tools** (with Portuguese descriptions), automated 6-stage device discovery and onboarding, a professional report engine (PDF, XLSX, CSV, JSON, Markdown), Role-Based Access Control (RBAC), two-phase cryptographic approvals, and multi-version compatibility.

---

## 🚀 Key Capabilities

- **100 Dedicated Tools:** Stable `snake_case` tool names, Pydantic data validation, and structured `ToolResult` outputs covering all Zabbix capabilities.
- **Automated 6-Stage Device Onboarding (Stages A to F):**
  1. *Controlled Discovery:* Scope-authorized CIDR scanning with rate limiting.
  2. *OS Fingerprinting:* OS classification (Linux, Windows, Network Appliances) with confidence scoring.
  3. *Reconciliation & Deduplication:* Matches against current Zabbix interfaces to prevent duplicates.
  4. *Planning & Preview:* Detailed preview with interfaces, host groups, and template linkage before committing.
  5. *Transactional Batch Creation:* Individual host creation with granular failure isolation.
  6. *Post-Onboarding Verification:* Validates interface status, enabled items, and initial metric arrival.
- **Enterprise Reporting Engine:** Direct export to corporate **PDF** documents (ReportLab tables and charts), multi-sheet **Excel (.xlsx)** spreadsheets, **CSV**, **JSON**, and **Markdown**.
- **Enterprise DevSecOps Security:**
  - RBAC modes: `somente_leitura` (default read-only), `operacional` (write/create), and `administrativo` (delete/users).
  - **Two-Phase Confirmation:** Destructive operations (host deletion, trigger purge) require parameter-bound HMAC-SHA256 tokens with a 15-minute TTL.
  - **Automatic Secret Redaction:** API tokens, passwords, and SNMP communities are masked as `[REDACTED]`.
  - **SSRF Prevention:** Blocks loopback subnets (`127.0.0.1`) and scans exceeding 1024 IPs.
  - **Local Immutable Audit Log:** Structured JSON Lines logging for all MCP calls (`audit_mcp.jsonl`).
- **Dynamic Version Compatibility:** Auto-detects Zabbix version via `apiinfo.version`, adapting HTTP headers (`Authorization: Bearer <token>` for Zabbix 7.0+ and body auth for <= 6.4).

---

## 📦 Quick Installation

```bash
git clone https://github.com/seu-usuario/zabbix-mcp-server.git
cd zabbix-mcp-server

python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\activate

pip install --upgrade pip
pip install -e ".[dev]"
```

### Configuration (`.env`)

```ini
ZABBIX_URL=http://your-zabbix-host:8080/api_jsonrpc.php
ZABBIX_TOKEN=your_api_token_here
ZABBIX_MCP_MODE=somente_leitura
```

### Test Suite Execution

```bash
pytest -v
```

---

## 🔌 Connecting to MCP Clients

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "zabbix": {
      "command": "python",
      "args": ["-m", "zabbix_mcp.server", "--transport", "stdio"],
      "env": {
        "ZABBIX_URL": "http://192.168.0.107:8080/api_jsonrpc.php",
        "ZABBIX_TOKEN": "your_token",
        "ZABBIX_MCP_MODE": "operacional"
      }
    }
  }
}
```

---

## 🛠️ The 100 Tools Summary

- **1. Auto Discovery (1-10):** Safe network probing, OS fingerprinting, deduplication, onboarding preview, and verification.
- **2. Hosts & Interfaces (11-20):** Listing, details, creation, update, approval-protected deletion, and interface management.
- **3. Data Collection (21-30):** Item configuration, history, trends, latest values, collection gap detection, and diagnostics.
- **4. Problems & Triggers (31-40):** Active problems, event history, trigger configuration, acknowledgement, and root-cause investigation.
- **5. Reports & Docs (41-50):** Executive summaries, availability, capacity, SLA, and PDF/Excel export.
- **6. Alerts & Actions (51-60):** Notification history, media types, controlled test sends, and flapping detection.
- **7. Services & Maps (61-70):** Business services, maintenance periods, and topology diagrams in Mermaid.
- **8. Inventory & Templates (71-80):** Hardware/software inventory, template linkage, and coverage auditing.
- **9. Native Discovery & Admin (81-90):** Network discovery rules, LLD, proxies, users, user roles, and audit logs.
- **10. Automation & AI (91-100):** Natural language translation to Zabbix queries, anomaly detection, approval workflow execution, and 360° health check.

---

## 📄 License

Distributed under the **MIT** License. See [LICENSE](LICENSE) for details.

