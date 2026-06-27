# RescueMind AI – 5-Minute Kaggle Demo Video Script

**Total Runtime:** 5:00 | **Format:** Screen recording + voiceover  
**Tone:** Professional, urgent, authoritative — this is life-saving technology

---

## [0:00–0:30] HOOK: The Problem (30 seconds)

**[VISUAL: Split screen — news footage of flood / cyclone damage on left; overwhelmed emergency call center on right. Then fade to black with text overlay.]**

**VOICEOVER:**
> "June 2024. Cyclone Remal. 5 million people in West Bengal with 12 hours to evacuate. Emergency lines jammed. Shelter locations unknown. Rescue teams with no priority list. Families separated with no way to find each other."

> "This is the reality of disaster response today. Information overload meets coordination failure at the worst possible moment."

> "What if AI agents could coordinate the chaos — in real time, in multiple languages, for every stakeholder from citizen to government?"

**[VISUAL: Fade to RescueMind AI logo]**

> "This is **RescueMind AI**."

---

## [0:30–1:00] THE SOLUTION (30 seconds)

**[VISUAL: High-level architecture diagram — 10 agents radiating from a central Coordinator]**

**VOICEOVER:**
> "RescueMind AI is a production-quality **multi-agent disaster response platform** built on Google Gemini. Ten specialized AI agents — monitored by a Coordinator — work in parallel to provide immediate, explainable, actionable guidance."

> "It serves **citizens** needing shelter, **emergency responders** prioritizing rescues, **NGOs** tracking resources, and **government agencies** allocating relief — all from one system."

> "Built for India. Available in **English, Tamil, and Hindi**. Deployable in minutes on Streamlit Cloud, Docker, or Google Cloud Run."

**[VISUAL: Switch to live running Streamlit dashboard]**

---

## [1:00–2:00] LIVE DEMO: DASHBOARD & MONITORING (60 seconds)

**[VISUAL: Streamlit app — Dashboard page]**

**VOICEOVER:**
> "The **Dashboard** gives commanders a unified situational picture."

**[ACTION: Point to active events section]**
> "Three active events — a Level 3 flood in Tirunelveli, a heatwave advisory across Madurai and Trichy, and a coastal surge watch for Chennai. Each is color-coded by severity."

**[ACTION: Scroll down to resource status]**
> "Resource status shows 5,000 food packets, 1,200 water cans, and 8 rescue boats — with real-time deployment percentages."

**[ACTION: Click Disaster Monitoring in sidebar]**
> "The **Monitoring page** shows the event timeline — every alert, every team deployment, every river gauge reading — in chronological order."

**[ACTION: Click Generate Alert button]**
> "Watch this. I select 'flood,' severity 4, and hit Generate Alert."

**[VISUAL: Alert box appears with trilingual message]**
> "In under one second, the Emergency Alert Agent generates a verified alert in English, Tamil, and Hindi — ready to broadcast via SMS, PA system, or social media."

---

## [2:00–3:00] LIVE DEMO: EMERGENCY ASSISTANT CHAT (60 seconds)

**[VISUAL: Emergency Assistant page — clean chat interface]**

**VOICEOVER:**
> "The **Emergency Assistant** is where citizens and responders get immediate guidance."

**[ACTION: Click quick query button "What should I do during a flood?"]**

**[VISUAL: Loading spinner → response appears]**

> "The Coordinator Agent classifies the intent, delegates to the Monitoring Agent for threat assessment and the Shelter Agent for nearby options, then synthesizes a unified plan."

**[ACTION: Point to response content]**
> "Notice the structured output: situation summary, prioritized actions with urgency tags — red for immediate, yellow for within an hour — and key emergency contacts."

**[ACTION: Click the Explainability Card expander]**
> "Every recommendation comes with a full **explainability card** — what was recommended, why, the confidence score, which data sources were used, and alternative actions. Citizens deserve to know *why* the AI says evacuate."

**[ACTION: Type in chat: "I need rescue – 4 people trapped, one elderly, flood water rising"]**

**[VISUAL: Response shows CRITICAL priority, teams dispatched, 108 contact highlighted]**

> "For rescue requests, the **Rescue Coordination Agent** runs a multi-factor priority algorithm — severity, vulnerability, number of people, accessibility. This scores as CRITICAL — 0.87 out of 1.0 — triggering NDRF team recommendations with expected response times."

---

## [3:00–3:45] LIVE DEMO: SHELTER FINDER & RESOURCES (45 seconds)

**[VISUAL: Shelter Finder page]**

**VOICEOVER:**
> "The **Shelter Finder** queries our database of Tamil Nadu relief camps."

**[ACTION: Click "Find Shelters" with default Tirunelveli coordinates]**

**[VISUAL: Three shelter cards appear, sorted by distance]**

> "Results are sorted by distance using the Haversine formula. Each card shows current occupancy, available capacity, facilities, and a direct contact number. The MCP Shelter Database server handles the query — decoupled from the agent so data sources can be swapped without code changes."

**[ACTION: Navigate to Resource Center]**

> "The **Resource Center** shows supply versus demand analysis. For 5,000 affected people, we calculate NDMA norms: 3 meals per person, 5 litres of water per day, one first aid kit per 10 people. Red bars show supply gaps — triggering automatic recommendations to request reinforcements."

---

## [3:45–4:30] TECHNICAL ARCHITECTURE DEEP DIVE (45 seconds)

**[VISUAL: Switch to architecture diagram — agent flow diagram]**

**VOICEOVER:**
> "Under the hood: **ten specialized agents** extend a shared BaseAgent class that handles Gemini integration, structured JSON output, retry logic with exponential backoff, and automatic database logging of every invocation."

**[VISUAL: MCP server diagram]**

> "Six **MCP servers** — weather, shelter, resources, government relief, medical knowledge, and emergency contacts — expose 20-plus tools via a unified MCPClient. Agents call MCP tools the same way Gemini calls functions — clean, decoupled, testable."

**[VISUAL: Security pipeline diagram]**

> "Every input passes through a **5-layer security pipeline** before touching any agent: rate limiting, input validation, prompt injection detection — catching 15 attack patterns — PII redaction for Aadhaar and PAN numbers, and disaster misinformation flagging."

**[VISUAL: Show test file briefly]**

> "The project includes **60-plus pytest tests** across unit, integration, agent workflow, MCP, and security categories — running in demo mode without API keys."

---

## [4:30–5:00] IMPACT & FUTURE ROADMAP (30 seconds)

**[VISUAL: Split: dashboard on left, roadmap bullet points fading in on right]**

**VOICEOVER:**
> "RescueMind AI is not a prototype. It's a production-quality system with real Tamil Nadu shelter data, real Indian government relief programs, real emergency helplines — deployable today on Streamlit Cloud or Google Cloud Run."

> "The roadmap extends to live IMD and NDMA API integration, satellite-based damage assessment via Google Earth Engine, voice interfaces for field responders, and push notifications for registered communities."

> "Most importantly — it's **explainable**. Every recommendation tells you why. In an emergency, trust in AI comes from transparency."

**[VISUAL: Final shot — logo + tagline]**

> "**RescueMind AI.** Because in a disaster, every second of coordination is a life saved."

> "All source code, documentation, deployment configs, and this demonstration are available in the Kaggle submission."

**[VISUAL: Fade to black with GitHub/Kaggle links]**

---

## PRODUCTION NOTES

| Section | Duration | Key Action |
|---------|----------|-----------|
| Hook / Problem | 0:00–0:30 | Stock footage or disaster photos |
| Solution overview | 0:30–1:00 | Architecture diagram |
| Dashboard + Monitoring | 1:00–2:00 | Live Streamlit demo |
| Emergency Assistant chat | 2:00–3:00 | Type 2 queries live |
| Shelter + Resources | 3:00–3:45 | Click through 2 pages |
| Technical deep dive | 3:45–4:30 | Code + diagrams |
| Impact + Roadmap | 4:30–5:00 | Logo close |

**Recording Tips:**
- Use Loom or OBS at 1920×1080
- Dark mode Streamlit theme looks best on video
- Pre-load the app to avoid cold start during demo
- Run in DEMO_MODE=true so no API latency
- Practice the chat queries — type slowly for viewer comprehension
- Add background music: soft, serious (not dramatic or distracting)
- Export at 60fps for smooth UI scrolling

**Voiceover Tips:**
- Speak at 130–140 words per minute (slightly faster than conversation)
- Pause 0.5 seconds after each section header
- Emphasize numbers: "**ten** specialized agents", "**60-plus** tests"
- End each demo action with a one-sentence insight
