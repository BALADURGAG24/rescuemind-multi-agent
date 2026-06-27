# 🆘 RescueMind AI
### Multi-Agent Disaster Response & Emergency Coordination System

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Pro-orange?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-AI_Agents_Capstone-20BEFF?logo=kaggle)](https://kaggle.com)

> **Built for the Kaggle AI Agents: Intensive Vibe Coding Capstone Project**

RescueMind AI is a production-quality, multi-agent AI platform that helps **citizens**, **emergency responders**, **NGOs**, and **government agencies** prepare for, respond to, and recover from natural disasters — powered by Google Gemini and a 6-server MCP architecture.

---

## ✨ What It Does

| For Citizens | For Responders | For Government |
|-------------|---------------|----------------|
| Real-time disaster alerts | Rescue priority scoring | Resource allocation |
| Nearest shelter finder | Team coordination | Damage assessment |
| First aid guidance | Medical routing | Relief program management |
| Evacuation route planning | Resource tracking | Situation reports |
| Relief program navigation | Incident logging | Recovery planning |

---

## 🏗️ Architecture

```
User Query
    ↓
🔒 Security Manager (5-layer: rate limit → injection → PII → misinfo → sanitize)
    ↓
🧠 Coordinator Agent (intent classification + task delegation)
    ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Specialized Agents (run in parallel based on intent)                │
│  🌊 Monitoring  │ 🚨 Alert  │ 🏠 Shelter  │ 🚁 Rescue │ 🏥 Medical │
│  📦 Resource    │ 🏗️ Damage │ 💰 Relief   │ 📋 Planning              │
└──────────────────────────────────────────────────────────────────────┘
    ↓
🔌 MCP Servers (6 servers, 20+ tools)
  ☁️ Weather  🏠 Shelter  📦 Resource  💰 Relief  🏥 Medical  📞 Contacts
    ↓
✨ Google Gemini 1.5 Pro / Flash
    ↓
📋 Unified Response Plan + Explainability Card
```

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/your-username/rescuemind-ai.git
cd rescuemind-ai

# Install
pip install -r requirements.txt

# Configure (demo mode works without API keys)
cp .env.example .env

# Initialize database
python -c "from database.schema import initialize_database; initialize_database()"

# Run
streamlit run app.py
```

Open **http://localhost:8501** — no API keys needed for demo mode!

---

## 📁 Project Structure

```
rescuemind/
│
├── 🤖 agents/
│   ├── base_agent.py          # Abstract base: Gemini, logging, explainability
│   ├── coordinator_agent.py   # Master orchestrator
│   ├── monitoring_agent.py    # Weather + disaster feeds
│   └── all_agents.py          # All 8 specialized agents
│
├── 🔌 mcp/
│   └── mcp_servers.py         # 6 MCP servers + unified client
│
├── 🗄️ database/
│   └── schema.py              # SQLite schema, seed data, helpers
│
├── 🔒 security/
│   └── security_manager.py    # Rate limiting, injection, PII, misinformation
│
├── ⚙️ config/
│   └── settings.py            # Central configuration
│
├── 📊 frontend/               # Page components (imported by app.py)
│
├── 🧪 tests/
│   └── test_rescuemind.py     # 60+ pytest tests
│
├── 📚 docs/
│   ├── architecture_diagrams.md  # Mermaid diagrams (5 diagrams)
│   ├── kaggle_writeup.md         # Competition writeup
│   ├── video_script.md           # 5-minute demo script
│   └── deployment_guide.md       # Deploy to 3 platforms
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage production container
├── docker-compose.yml         # Local multi-service setup
├── cloudrun.yaml              # Google Cloud Run config
├── .env.example               # Environment variable template
└── .streamlit/
    └── config.toml            # Streamlit theme + server config
```

---

## 🤖 The 10 Agents

### Coordinator Agent
The central orchestrator. Classifies user intent using Gemini, delegates to 1–4 relevant specialized agents in parallel, synthesizes outputs into a unified response plan with priority-ordered actions and emergency contacts.

### Disaster Monitoring Agent
Fetches weather from OpenWeatherMap, queries disaster event database, runs threat assessment using Gemini (or rule-based fallback). Returns threat level 1–5, primary hazard type, and immediate protective actions.

### Emergency Alert Agent
Generates verified emergency alerts in **English, Tamil (தமிழ்), and Hindi (हिंदी)**. Templates ensure zero-latency delivery even without LLM. Includes helplines, do/avoid lists, issuing authority.

### Shelter & Evacuation Agent
Queries shelter database, calculates distance using Haversine formula, filters by disaster type compatibility, returns ranked list with capacity, occupancy percentage, facilities, and contact information.

### Rescue Coordination Agent
Multi-factor weighted priority scoring: severity (30%), injury presence (25%), children (15%), elderly (10%), number of people (10%), time urgency (5%), accessibility (5%). Maps score to CRITICAL/HIGH/MODERATE/LOW.

### Medical Assistance Agent
Condition identification from query keywords. Step-by-step first aid protocols for drowning, heat stroke, fractures, wounds. Hospital recommendations. Emergency contact routing (108 ambulance).

### Resource Allocation Agent
Calculates requirements using NDMA norms (3 meals/person, 5L water/day, 1 kit per 10 people). Compares against live inventory. Identifies supply gaps. Recommends redistribution from adjacent depots.

### Damage Assessment Agent
Severity-based infrastructure damage model calibrated for Indian disaster patterns. Scores infrastructure, housing, agriculture, and roads as damage percentages. Generates phased recovery timeline.

### Government Relief Agent
Matches disaster type to relevant government schemes and NGO programs. Returns eligibility criteria, benefit amounts, application URLs, and direct contact numbers from seeded database of real Indian programs.

### Planning Agent
Generates comprehensive preparedness, response, and recovery plans with phased timelines, resource checklists, key contacts, and step-by-step action items tailored to disaster type and user role.

---

## 🔌 MCP Servers

| Server | Port | Tools |
|--------|------|-------|
| ☁️ Weather & Disaster | 8001 | `get_current_weather`, `get_disaster_alerts`, `get_flood_risk`, `get_active_events` |
| 🏠 Shelter Database | 8002 | `find_nearby_shelters`, `get_shelter_details`, `update_occupancy`, `get_capacity_summary` |
| 📦 Resource Management | 8003 | `get_resource_inventory`, `allocate_resources`, `get_supply_gaps`, `update_quantity` |
| 💰 Government Relief | 8004 | `get_relief_programs`, `check_eligibility`, `submit_application` |
| 🏥 Medical Knowledge | 8005 | `get_first_aid_guidance`, `find_nearby_hospitals`, `get_emergency_contacts` |
| 📞 Emergency Contacts | 8006 | `get_emergency_contacts`, `get_rescue_teams` |

---

## 🔒 Security Features

- **Rate Limiting** — Sliding window, 60 req/min, per user ID
- **Input Validation** — Length limits, HTML stripping, type checking
- **Prompt Injection Detection** — 15 compiled regex patterns for DAN, role-switching, delimiter injection
- **PII Redaction** — Auto-detects and redacts Aadhaar, PAN, credit cards, phone, email before LLM
- **Misinformation Detection** — Flags disaster-related misinformation with source warnings
- **API Key Security** — `.env` only, never in code; Streamlit Cloud secrets; Docker environment
- **Non-root Container** — Dedicated `rescuemind` user in Docker
- **Parameterized SQL** — No string formatting in queries

---

## 📊 Explainability

Every AI recommendation includes a structured explainability card:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Coordinator Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Recommendation:
  Evacuate to Shelter SH001 (2.1km) via Palayamkottai Road

💡 Why this was recommended:
  Flood threat level CRITICAL (4/5). Thamirabarani river above
  danger mark. Shelter has 380 available spots with medical aid.

📊 Confidence: 87%  |  ⚠️ Risk Level: CRITICAL

🗄️ Data Sources: IMD, TN SDMA, RescueMind Shelter Database

🔄 Alternative Actions:
  • Move to upper floors if evacuation route blocked
  • Shelter SH002 (Palayamkottai) – 3.4km, 215 spots
  • Contact 1077 (Flood Helpline)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🌐 Multi-Language Support

| Language | Code | Coverage |
|----------|------|----------|
| English | `en` | Full |
| Tamil (தமிழ்) | `ta` | Alerts, UI labels, LLM responses |
| Hindi (हिंदी) | `hi` | Alerts, UI labels, LLM responses |

---

## 🧪 Testing

```bash
# Run all 60+ tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Test categories:
# TestDatabase          – Schema, seed data, integrity
# TestSecurity          – All 5 security layers
# TestBaseAgent         – Response structure, explainability
# TestAgentWorkflows    – Each of 9 specialized agents
# TestCoordinatorAgent  – Orchestration and delegation
# TestMCPServers        – All 6 servers, 15 tool calls
# TestDistanceCalculations – Haversine accuracy
# TestIntegration       – End-to-end workflows
# TestConfiguration     – Settings completeness
```

---

## 🚢 Deployment

| Platform | Time | Cost | Command |
|----------|------|------|---------|
| Local | 2 min | Free | `streamlit run app.py` |
| Streamlit Cloud | 5 min | Free | Push to GitHub → connect |
| Docker | 5 min | Hosting | `docker-compose up -d` |
| Google Cloud Run | 12 min | ~$0 (free tier) | `gcloud run deploy` |

See [docs/deployment_guide.md](docs/deployment_guide.md) for full instructions.

---

## 📋 Kaggle Competition Criteria

| Criterion | ✅ Implementation |
|-----------|-----------------|
| Multi-Agent System | 10 agents, Coordinator orchestration, parallel delegation |
| MCP Server Integration | 6 servers, 20+ tools, unified MCPClient |
| Agent Skills | Priority scoring, first-aid lookup, shelter discovery, planning |
| Security Features | 5-layer pipeline: rate limit, injection, PII, misinfo, sanitize |
| Deployability | Streamlit Cloud, Docker, Google Cloud Run — all configured |
| Explainability | Every recommendation: confidence + sources + reason + alternatives |

---

## 🛣️ Roadmap

- [ ] Live IMD + NDMA API integration
- [ ] Google Earth Engine satellite damage analysis
- [ ] Voice interface for field responders
- [ ] Progressive Web App (offline mode)
- [ ] Push notifications for registered communities
- [ ] NDRF dispatch API integration
- [ ] Crowdsourced incident reporting
- [ ] Multi-state shelter database expansion

---

## 📸 Screenshots

> *Screenshots from the running Streamlit application*

| Dashboard | Emergency Assistant | Shelter Finder |
|-----------|--------------------| ---------------|
| Active events, resources, agent activity | AI chat with explainability cards | Shelters sorted by distance |

| Disaster Monitoring | Resource Center | Relief Programs |
|--------------------| ---------------| ----------------|
| Event timeline, weather, risk map | Supply vs demand analysis | Government schemes |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Run tests: `pytest tests/ -v`
4. Submit a pull request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- **Google Gemini** — LLM backbone
- **NDMA India** — Disaster management protocols
- **India Meteorological Department** — Weather alert standards
- **Tamil Nadu SDMA** — Regional disaster data
- **Indian Red Cross** — First aid guidelines
- **Streamlit** — Application framework
- **Kaggle** — Competition platform

---

## 📞 Emergency Contacts (India)

| Service | Number |
|---------|--------|
| 🚨 National Emergency | **112** |
| 🏥 Ambulance | **108** |
| 🌊 Flood Helpline | **1077** |
| 🔥 Fire | **101** |
| 👮 Police | **100** |
| 🌀 Disaster Management | **1079** |

---

*RescueMind AI — Because in a disaster, every second of coordination is a life saved.*
