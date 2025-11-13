# Kali Agents - "At Your Service" ?

![Kali Agents Logo](https://img.shields.io/badge/Kali%20Agents-At%20Your%20Service-red?style=for-the-badge&logo=kali-linux)

**Intelligent orchestration system for Kali Linux cybersecurity tools using MCP and LangGraph**

## ? Vision

Transform Kali Linux from a collection of tools into an intelligent cybersecurity assistant that orchestrates complex security workflows automatically.

## ? What is Kali Agents?

Instead of manually running:
```bash
nmap -sV target.com
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt
sqlmap -u "http://target.com/login.php" --forms
```

Simply say:
```bash
kali-agents pentest --target target.com --scope full
```

And watch as intelligent agents orchestrate your entire security assessment!

## ?? Architecture

```
???????????????????????????????????????????????????????????????
?                     KALI COMMAND CENTER                     ?
?                   "Agents at Your Service"                  ?
???????????????????????????????????????????????????????????????
                              ?
                              ?
???????????????????????????????????????????????????????????????
?                    SUPERVISOR AGENT                         ?
?           ? Main Orchestrator                              ?
???????????????????????????????????????????????????????????????
                              ?
            ?????????????????????????????????????
            ?                 ?                 ?
    ????????????????? ????????????????? ?????????????????
    ? NETWORK AGENT ? ?   WEB AGENT   ? ? FORENSIC AGENT?
    ?      ?       ? ?      ?       ? ?      ?       ?
    ????????????????? ????????????????? ?????????????????
            ?                 ?                 ?
            ?                 ?                 ?
    ????????????????? ????????????????? ?????????????????
    ?   VULN AGENT  ? ? SOCIAL AGENT  ? ? REPORT AGENT  ?
    ?      ??       ? ?      ?       ? ?      ?       ?
    ????????????????? ????????????????? ?????????????????
```

## ? Specialized Agents

### ? Network Agent - "Network Recon at Your Service"
- **Tools**: nmap, masscan, zmap, netdiscover, arp-scan
- **Purpose**: Network discovery, port scanning, OS detection

### ? Web Agent - "Web Hacking at Your Service"
- **Tools**: gobuster, nikto, burp suite, wpscan, dirb
- **Purpose**: Web application testing, directory enumeration

### ?? Vulnerability Agent - "Exploit Research at Your Service"
- **Tools**: sqlmap, metasploit, searchsploit, nuclei
- **Purpose**: Vulnerability assessment and exploitation

### ? Forensic Agent - "Digital Forensics at Your Service"
- **Tools**: volatility, autopsy, binwalk, wireshark
- **Purpose**: Digital forensics and malware analysis

### ? Social Agent - "Social Engineering at Your Service"
- **Tools**: SET, maltego, theHarvester, shodan
- **Purpose**: OSINT and social engineering

### ? Report Agent - "Professional Reports at Your Service"
- **Purpose**: Automated professional penetration testing reports

## ? Getting Started

### Prerequisites
- Kali Linux (recommended)
- Python 3.9+
- Ollama (for local LLM hosting)

### Installation
```bash
git clone https://github.com/Simon-Terrien/kali-agents.git
cd kali-agents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # tooling for tests (includes pytest-cov)
```

### Running the Data Server
The Data MCP server stores scan results in a local SQLite database. Copy
`.env.example` to `.env` and adjust `DB_PATH` if needed, then start the server:

```bash
python -m src.mcp_servers.data_server
```

### Quick Start
```bash
# Basic network scan
kali-agents recon --target 192.168.1.0/24

# Web application test
kali-agents web --url https://target.com --deep

# Full penetration test
kali-agents pentest --target company.com --scope full

# OSINT gathering
kali-agents osint --target "John Doe" --company "ACME Corp"
```

### Running Tests
Create a development environment and install test dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Then execute the tests (coverage options are preconfigured in `pyproject.toml`):

```bash
./test.sh
```

### REST API (Web & Network Scans)
Spin up the FastAPI server to drive scans from tools like AG-UI or custom dashboards:

```bash
export KALI_AGENTS_API_KEY=dev-token
uvicorn src.api.main:app --reload
```

Call the endpoints with Bearer auth:

```bash
curl -X POST http://127.0.0.1:8000/network/scan \
  -H "Authorization: Bearer $KALI_AGENTS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.10", "scan_type": "stealth"}'
```

Interactive docs are available at `http://127.0.0.1:8000/docs`.

### Docker & Compose
Build portable images (API + CLI) with the provided multi-stage Dockerfile:

```bash
docker build --target api -t kali-agents-api .
docker build --target cli -t kali-agents-cli .
```

Run the API container (exposes FastAPI + WebSocket endpoints):

```bash
docker run -p 8000:8000 -e KALI_AGENTS_API_KEY=dev-token kali-agents-api
```

Or orchestrate the API, CLI, and data MCP server together:

```bash
docker compose up --build
```

Mount `.env`/data folders via `volumes` in `docker-compose.yml` to keep secrets and scan outputs outside the container.

## ? Use Cases

### For Penetration Testers
- Automated reconnaissance workflows
- Consistent testing methodologies
- Professional report generation

### For Red Teams
- Complex attack simulation
- Multi-vector campaign orchestration
- Tactical AI assistance

### For Blue Teams
- Automated defensive testing
- Security validation
- Intelligent attacker simulation

### For Education
- Interactive learning environments
- Automated demonstrations
- Dynamic training scenarios

## ?? Technology Stack

- **Orchestration**: LangGraph for multi-agent workflows
- **Tool Integration**: Model Context Protocol (MCP)
- **AI Engine**: Ollama with Llama models
- **Backend**: FastAPI for web interface
- **Frontend**: React-based dashboard

## ? Development Status

- [ ] Sprint 0: Core Architecture ?
- [ ] Sprint 1: Network & Web Agents
- [ ] Sprint 2: Vulnerability Assessment
- [ ] Sprint 3: Forensics & OSINT
- [ ] Sprint 4: Report Generation
- [ ] Sprint 5: Web Interface

## ? Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

- Read `AGENTS.md` for day-to-day repository guidelines (structure, commands, testing).
- Consult `CONTEXT.MD` for the Pydantic AI reference materials that inform our agent patterns.
- Skim `memory.md` before each work session to inherit the latest testing notes, priorities, and regressions.

## ? License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ?? Disclaimer

This tool is for educational and authorized penetration testing purposes only. Users are responsible for complying with all applicable laws and regulations.

## ? Philosophy

**"Kali Agents at Your Service"** - Because ethical hackers deserve tools as intelligent as they are.

*Transforming Kali Linux from a toolbox into an intelligent cybersecurity assistant.*

---

? Star this repository if you find it useful!
