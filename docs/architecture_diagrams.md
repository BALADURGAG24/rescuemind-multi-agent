# RescueMind AI – Architecture Diagrams

## 1. Multi-Agent Interaction Flow

```mermaid
flowchart TB
    USER([👤 User / Citizen / Responder])
    SEC[🔒 Security Manager<br/>Rate Limit · Injection Detection<br/>PII Filter · Misinformation Check]
    COORD[🧠 Coordinator Agent<br/>Intent Classification<br/>Task Delegation<br/>Response Synthesis]

    subgraph AGENTS["Specialized Agents"]
        MON[🌊 Disaster Monitoring<br/>Weather · Threat Level]
        ALERT[🚨 Emergency Alert<br/>Multilingual Notifications]
        SHEL[🏠 Shelter & Evacuation<br/>Nearest Shelter · Routes]
        RESC[🚁 Rescue Coordination<br/>Priority Scoring · Teams]
        MED[🏥 Medical Assistance<br/>First Aid · Hospitals]
        RES[📦 Resource Allocation<br/>Supply · Distribution]
        DAM[🏗️ Damage Assessment<br/>Impact · Recovery]
        REL[💰 Government Relief<br/>Programs · Applications]
        PLAN[📋 Planning Agent<br/>Preparedness · Recovery]
    end

    subgraph MCP["MCP Servers"]
        MCP1[☁️ Weather & Disaster]
        MCP2[🏠 Shelter Database]
        MCP3[📦 Resource Management]
        MCP4[💰 Government Relief]
        MCP5[🏥 Medical Knowledge]
        MCP6[📞 Emergency Contacts]
    end

    DB[(🗄️ SQLite Database<br/>9 Tables)]
    GEMINI[✨ Google Gemini<br/>1.5 Pro / Flash]

    USER -->|Query| SEC
    SEC -->|Sanitized Input| COORD
    COORD --> MON & ALERT & SHEL & RESC & MED & RES & DAM & REL & PLAN
    MON --> MCP1
    SHEL --> MCP2
    RES --> MCP3
    REL --> MCP4
    MED --> MCP5
    ALERT --> MCP6
    AGENTS --> GEMINI
    AGENTS --> DB
    COORD -->|Unified Plan| USER

    style COORD fill:#1e3a5f,color:#60a5fa
    style SEC fill:#3b1f1f,color:#fca5a5
    style GEMINI fill:#1f3b1f,color:#6ee7b7
    style DB fill:#2d1f3f,color:#d8b4fe
```

---

## 2. MCP Architecture

```mermaid
flowchart LR
    subgraph AGENTS["AI Agents"]
        A1[Monitoring Agent]
        A2[Shelter Agent]
        A3[Resource Agent]
        A4[Relief Agent]
        A5[Medical Agent]
        A6[Alert Agent]
    end

    CLIENT[🔌 MCP Client<br/>Unified Interface]

    subgraph SERVERS["MCP Servers"]
        S1["☁️ Weather & Disaster MCP<br/>Port 8001<br/>Tools: get_weather · get_alerts · flood_risk"]
        S2["🏠 Shelter Database MCP<br/>Port 8002<br/>Tools: find_nearby · get_details · update_occupancy"]
        S3["📦 Resource Management MCP<br/>Port 8003<br/>Tools: get_inventory · allocate · get_gaps"]
        S4["💰 Government Relief MCP<br/>Port 8004<br/>Tools: get_programs · check_eligibility · apply"]
        S5["🏥 Medical Knowledge MCP<br/>Port 8005<br/>Tools: first_aid · find_hospitals · contacts"]
        S6["📞 Emergency Contact MCP<br/>Port 8006<br/>Tools: get_contacts · get_rescue_teams"]
    end

    subgraph EXTERNAL["External APIs"]
        E1[OpenWeatherMap]
        E2[IMD Feed]
        E3[ReliefWeb API]
        E4[NDMA Portal]
    end

    AGENTS --> CLIENT
    CLIENT --> S1 & S2 & S3 & S4 & S5 & S6
    A1 --> CLIENT
    A2 --> CLIENT
    A3 --> CLIENT
    A4 --> CLIENT
    A5 --> CLIENT
    A6 --> CLIENT
    S1 --> E1 & E2
    S4 --> E3 & E4

    style CLIENT fill:#1e3a5f,color:#60a5fa
```

---

## 3. Deployment Architecture

```mermaid
flowchart TB
    subgraph INTERNET["Internet"]
        USER([👤 Users])
        CDN[CloudFlare CDN]
    end

    subgraph CLOUD["Google Cloud Platform"]
        LB[Cloud Load Balancer<br/>HTTPS · SSL Termination]
        subgraph RUN["Cloud Run (Auto-scaling)"]
            APP1[RescueMind App<br/>Instance 1]
            APP2[RescueMind App<br/>Instance 2]
            APP3[RescueMind App<br/>Instance N]
        end
        SECRETS[Secret Manager<br/>API Keys · Credentials]
        STORAGE[Cloud Storage<br/>Static Assets · Backups]
        LOGS[Cloud Logging<br/>& Monitoring]
    end

    subgraph LOCAL["Local / Streamlit Cloud"]
        ST[Streamlit Cloud<br/>Free Tier Option]
        SQLITE[(SQLite DB<br/>Persistent Volume)]
    end

    USER --> CDN --> LB
    LB --> APP1 & APP2 & APP3
    APP1 & APP2 & APP3 --> SECRETS
    APP1 & APP2 & APP3 --> STORAGE
    APP1 & APP2 & APP3 --> LOGS
    USER -.->|Alternative| ST
    ST --> SQLITE

    style CLOUD fill:#0f2040,color:#60a5fa
    style LOCAL fill:#1f2f0f,color:#6ee7b7
```

---

## 4. Emergency Response Workflow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant SEC as 🔒 Security
    participant COORD as 🧠 Coordinator
    participant MON as 🌊 Monitor
    participant SHEL as 🏠 Shelter
    participant RESC as 🚁 Rescue
    participant MED as 🏥 Medical
    participant DB as 🗄️ Database
    participant GEM as ✨ Gemini

    U->>SEC: "I need rescue – 4 people trapped, flood"
    SEC->>SEC: Rate limit check
    SEC->>SEC: Injection detection
    SEC->>SEC: PII redaction
    SEC-->>COORD: Sanitized input ✅

    COORD->>GEM: Classify intent
    GEM-->>COORD: {intents: [rescue, medical, shelter]}

    par Parallel Agent Execution
        COORD->>MON: Assess current threat
        MON->>DB: Query active events
        MON-->>COORD: Threat Level 4 / Critical

        COORD->>RESC: Calculate priority score
        RESC->>RESC: Multi-factor scoring
        RESC-->>COORD: Score 0.87 / CRITICAL

        COORD->>SHEL: Find nearest shelter
        SHEL->>DB: Query shelters by location
        SHEL-->>COORD: SH001 – 2.1km, 380 spots

        COORD->>MED: Emergency medical guidance
        MED-->>COORD: First aid steps + 108
    end

    COORD->>GEM: Synthesize unified plan
    GEM-->>COORD: {situation, priority_actions, contacts}

    COORD->>DB: Log advisory history
    COORD-->>U: ✅ Unified response + explainability card

    Note over U,GEM: Total latency: ~3-6s (demo) / ~8-15s (live Gemini)
```

---

## 5. Database Entity Relationship

```mermaid
erDiagram
    USERS {
        text user_id PK
        text name
        text role
        text language
        real location_lat
        real location_lon
    }

    DISASTER_EVENTS {
        text event_id PK
        text disaster_type
        text title
        int severity
        text status
        text location_name
    }

    EMERGENCY_REQUESTS {
        text request_id PK
        text user_id FK
        text request_type
        int severity
        real priority_score
        text status
    }

    SHELTERS {
        text shelter_id PK
        text name
        int capacity
        int current_occupancy
        text district
    }

    RESOURCE_INVENTORY {
        text resource_id PK
        text resource_type
        text name
        real quantity
        text unit
    }

    AGENT_LOGS {
        text log_id PK
        text agent_name
        text action
        real confidence
        int duration_ms
    }

    ADVISORY_HISTORY {
        text advisory_id PK
        text user_id FK
        text advisory_type
        text recommendation
        real confidence
    }

    RELIEF_PROGRAMS {
        text program_id PK
        text name
        text provider
        text eligibility
    }

    RELIEF_APPLICATIONS {
        text application_id PK
        text user_id FK
        text program_id FK
        text status
    }

    USERS ||--o{ EMERGENCY_REQUESTS : "submits"
    USERS ||--o{ ADVISORY_HISTORY : "receives"
    USERS ||--o{ RELIEF_APPLICATIONS : "applies"
    RELIEF_PROGRAMS ||--o{ RELIEF_APPLICATIONS : "has"
    DISASTER_EVENTS ||--o{ EMERGENCY_REQUESTS : "triggers"
    DISASTER_EVENTS ||--o{ AGENT_LOGS : "generates"
```
