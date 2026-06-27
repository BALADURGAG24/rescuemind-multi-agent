"""
RescueMind AI – Main Streamlit Application
Multi-Agent Disaster Response & Emergency Coordination System

Pages:
  1. 🏠 Dashboard          – Active disasters, risk map, resource status
  2. 🚨 Emergency Assistant – AI chat for disaster guidance
  3. 🌊 Disaster Monitoring – Real-time alerts and event timeline
  4. 🏠 Shelter Finder      – Nearby shelters with capacity
  5. 📦 Resource Center     – Supply status and allocation
  6. 💰 Relief Programs     – Government and NGO assistance
  7. ⚙️ Settings           – Language and preferences
"""

import sys
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# ─── Page Configuration (MUST be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="RescueMind AI",
    page_icon="🆘",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://ndma.gov.in",
        "Report a bug": None,
        "About": "RescueMind AI – Multi-Agent Disaster Response System v1.0",
    },
)

# ─── Initialize Database & Logging ────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@st.cache_resource
def init_database():
    from database.schema import initialize_database
    initialize_database()
    return True

try:
    init_database()
except Exception as e:
    st.warning(f"Database init warning: {e}")

# ─── Translations ──────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "app_name": "RescueMind AI",
        "tagline": "Multi-Agent Disaster Response & Emergency Coordination",
        "emergency_assistant": "Emergency Assistant",
        "ask_placeholder": "Ask about flood safety, nearest shelter, rescue request, first aid...",
        "send": "Send",
        "thinking": "Agents are analyzing your query...",
        "dashboard": "Dashboard",
        "shelter_finder": "Shelter Finder",
        "monitoring": "Disaster Monitoring",
        "resources": "Resource Center",
        "relief": "Relief Programs",
        "settings": "Settings",
        "emergency_contacts": "Emergency Contacts",
        "active_disasters": "Active Disasters",
        "severity": "Severity",
        "find_shelter": "Find Nearest Shelter",
        "your_location": "Your Location",
    },
    "ta": {
        "app_name": "ரெஸ்க்யூமைண்ட் AI",
        "tagline": "பல முகவர் பேரிடர் மறுமொழி அமைப்பு",
        "emergency_assistant": "அவசர உதவியாளர்",
        "ask_placeholder": "வெள்ள பாதுகாப்பு, அருகிலுள்ள தங்குமிடம், மீட்பு கோரிக்கை பற்றி கேளுங்கள்...",
        "send": "அனுப்பு",
        "thinking": "முகவர்கள் உங்கள் கோரிக்கையை பகுப்பாய்வு செய்கின்றனர்...",
        "dashboard": "டாஷ்போர்டு",
        "shelter_finder": "தங்குமிட தேடல்",
        "monitoring": "பேரிடர் கண்காணிப்பு",
        "resources": "வள மையம்",
        "relief": "நிவாரண திட்டங்கள்",
        "settings": "அமைப்புகள்",
        "emergency_contacts": "அவசர தொடர்புகள்",
        "active_disasters": "செயல்பாட்டில் உள்ள பேரிடர்கள்",
        "severity": "தீவிரம்",
        "find_shelter": "அருகிலுள்ள தங்குமிடம் கண்டறிக",
        "your_location": "உங்கள் இருப்பிடம்",
    },
    "hi": {
        "app_name": "रेस्क्यूमाइंड AI",
        "tagline": "बहु-एजेंट आपदा प्रतिक्रिया और आपातकालीन समन्वय",
        "emergency_assistant": "आपातकालीन सहायक",
        "ask_placeholder": "बाढ़ सुरक्षा, निकटतम आश्रय, बचाव अनुरोध के बारे में पूछें...",
        "send": "भेजें",
        "thinking": "एजेंट आपकी क्वेरी का विश्लेषण कर रहे हैं...",
        "dashboard": "डैशबोर्ड",
        "shelter_finder": "आश्रय खोजक",
        "monitoring": "आपदा निगरानी",
        "resources": "संसाधन केंद्र",
        "relief": "राहत कार्यक्रम",
        "settings": "सेटिंग्स",
        "emergency_contacts": "आपातकालीन संपर्क",
        "active_disasters": "सक्रिय आपदाएं",
        "severity": "गंभीरता",
        "find_shelter": "निकटतम आश्रय खोजें",
        "your_location": "आपका स्थान",
    },
}


def t(key: str) -> str:
    """Translate a key to the current language."""
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ─── CSS Styling ───────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
/* ─── Global ─── */
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #1a1f2e !important; border-right: 1px solid #2d3748; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #e2e8f0 !important; }
p, li { color: #cbd5e0; }

/* ─── Metric Cards ─── */
.metric-card {
    background: linear-gradient(135deg, #1e2533 0%, #252d3d 100%);
    border: 1px solid #2d3748; border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.metric-value { font-size: 2rem; font-weight: 700; color: #fff; }
.metric-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-delta { font-size: 0.8rem; margin-top: 0.3rem; }

/* ─── Severity Badges ─── */
.badge-low      { background: #064e3b; color: #6ee7b7; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; }
.badge-moderate { background: #78350f; color: #fcd34d; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; }
.badge-high     { background: #7c2d12; color: #fb923c; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; }
.badge-critical { background: #7f1d1d; color: #fca5a5; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; }
.badge-extreme  { background: #3b0764; color: #d8b4fe; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; }

/* ─── Alert Boxes ─── */
.alert-critical { background: rgba(239,68,68,0.15); border-left: 4px solid #ef4444;
                  padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
.alert-high     { background: rgba(249,115,22,0.12); border-left: 4px solid #f97316;
                  padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
.alert-moderate { background: rgba(245,158,11,0.12); border-left: 4px solid #f59e0b;
                  padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
.alert-info     { background: rgba(59,130,246,0.12); border-left: 4px solid #3b82f6;
                  padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }

/* ─── Chat ─── */
.chat-user      { background: #1e3a5f; border-radius: 12px 12px 4px 12px;
                  padding: 0.8rem 1rem; margin: 0.5rem 0; max-width: 80%; margin-left: auto; }
.chat-assistant { background: #1e2533; border: 1px solid #2d3748;
                  border-radius: 4px 12px 12px 12px;
                  padding: 0.8rem 1rem; margin: 0.5rem 0; max-width: 90%; }

/* ─── Cards ─── */
.card { background: #1e2533; border: 1px solid #2d3748; border-radius: 12px;
        padding: 1.2rem; margin-bottom: 1rem; }

/* ─── Emergency strip ─── */
.emergency-strip { background: linear-gradient(90deg, #ef4444, #dc2626);
                   color: white; padding: 0.6rem 1rem; border-radius: 8px;
                   font-weight: 700; text-align: center; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.85; } }

/* ─── Sidebar nav ─── */
.nav-item { padding: 0.5rem 0.8rem; border-radius: 8px; margin: 2px 0;
            cursor: pointer; transition: background 0.2s; color: #94a3b8; }
.nav-item:hover { background: #2d3748; color: #e2e8f0; }
.nav-item.active { background: #1e3a5f; color: #60a5fa; font-weight: 600; }

/* ─── Progress bars ─── */
.stProgress > div > div > div { background: linear-gradient(90deg, #3b82f6, #60a5fa); }

/* ─── Shelter cards ─── */
.shelter-card { background: #1e2533; border: 1px solid #2d3748;
                border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; }
.shelter-card:hover { border-color: #3b82f6; box-shadow: 0 0 12px rgba(59,130,246,0.2); }

/* ─── Button overrides ─── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem;
    font-weight: 600; transition: all 0.2s;
}
.stButton > button:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)


# ─── Session State Defaults ────────────────────────────────────────────────────
def init_session():
    defaults = {
        "language": "en",
        "chat_history": [],
        "session_id": str(uuid.uuid4())[:8],
        "user_id": f"user_{uuid.uuid4().hex[:6]}",
        "user_location": "Tirunelveli, Tamil Nadu",
        "user_lat": 8.7139,
        "user_lon": 77.7567,
        "current_page": "Dashboard",
        "last_disaster_type": "flood",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem;">
  <div style="font-size:2.5rem;">🆘</div>
  <div style="font-size:1.3rem; font-weight:800; color:#e2e8f0;">RescueMind AI</div>
  <div style="font-size:0.75rem; color:#94a3b8;">v1.0 | Multi-Agent System</div>
</div>
<hr style="border-color:#2d3748; margin:0.5rem 0 1rem;">
""", unsafe_allow_html=True)

        # Emergency strip
        st.markdown('<div class="emergency-strip">⚠️ ACTIVE: Flood Watch – Tirunelveli</div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation
        pages = [
            ("🏠", "Dashboard"),
            ("🚨", "Emergency Assistant"),
            ("🌊", "Disaster Monitoring"),
            ("🏠", "Shelter Finder"),
            ("📦", "Resource Center"),
            ("💰", "Relief Programs"),
            ("⚙️", "Settings"),
        ]
        st.markdown("**Navigation**")
        for icon, page in pages:
            is_active = st.session_state.current_page == page
            style = "background:#1e3a5f; color:#60a5fa; font-weight:600;" if is_active else "color:#94a3b8;"
            if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

        st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)

        # Emergency Contacts
        st.markdown("**🆘 Emergency Contacts**")
        contacts = [("🚨 Emergency", "112"), ("🏥 Ambulance", "108"),
                    ("🌊 Flood Help", "1077"), ("🔥 Fire", "101"),
                    ("👮 Police", "100"), ("🌀 Disaster", "1079")]
        for label, num in contacts:
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; padding:2px 0;">'
                f'<span style="color:#94a3b8; font-size:0.8rem;">{label}</span>'
                f'<span style="color:#60a5fa; font-weight:700; font-size:0.85rem;">{num}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
        lang = st.selectbox("🌐 Language", ["English", "தமிழ்", "हिंदी"],
                            key="lang_select",
                            index=["English","தமிழ்","हिंदी"].index(
                                {"en":"English","ta":"தமிழ்","hi":"हिंदी"}.get(st.session_state.language,"English")
                            ))
        lang_map = {"English": "en", "தமிழ்": "ta", "हिंदी": "hi"}
        st.session_state.language = lang_map[lang]


# ─── PAGE: DASHBOARD ──────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown("## 🏠 Disaster Response Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} IST*")

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="metric-card">
<div class="metric-label">Active Events</div>
<div class="metric-value">3</div>
<div class="metric-delta" style="color:#f97316;">↑ 1 new today</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-card">
<div class="metric-label">People Affected</div>
<div class="metric-value">12,400</div>
<div class="metric-delta" style="color:#ef4444;">↑ 2,100 since yesterday</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="metric-card">
<div class="metric-label">Shelters Active</div>
<div class="metric-value">6</div>
<div class="metric-delta" style="color:#22c55e;">✓ 1,285 / 4,700 capacity used</div>
</div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="metric-card">
<div class="metric-label">Rescue Requests</div>
<div class="metric-value">47</div>
<div class="metric-delta" style="color:#f97316;">⚠ 12 pending priority</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 🌊 Active Disaster Events")
        events = [
            {"title": "Thamirabarani River Flooding", "type": "🌊 Flood", "location": "Tirunelveli",
             "severity": 3, "status": "🔴 Active", "label": "high"},
            {"title": "Severe Heatwave", "type": "🔥 Heatwave", "location": "Madurai, Trichy",
             "severity": 2, "status": "🟡 Monitoring", "label": "moderate"},
            {"title": "Coastal Surge Warning", "type": "🌊 Cyclone Watch", "location": "Chennai Coast",
             "severity": 2, "status": "🟡 Monitoring", "label": "moderate"},
        ]
        for ev in events:
            badge_color = {"high": "#ef4444", "moderate": "#f59e0b", "low": "#22c55e"}.get(ev["label"], "#94a3b8")
            st.markdown(f"""
<div class="card" style="border-left: 4px solid {badge_color};">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <span style="font-size:0.9rem; font-weight:700; color:#e2e8f0;">{ev['type']} – {ev['title']}</span><br>
      <span style="font-size:0.8rem; color:#94a3b8;">📍 {ev['location']}</span>
    </div>
    <div style="text-align:right;">
      <div style="color:{badge_color}; font-weight:700;">Level {ev['severity']}/5</div>
      <div style="font-size:0.8rem; color:#94a3b8;">{ev['status']}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("### 📊 Resource Status Overview")
        resources = [
            ("🍱 Food Packets", 5000, 3000, "wheat"),
            ("💧 Water Cans (20L)", 1200, 800, "blue"),
            ("💊 First Aid Kits", 300, 150, "green"),
            ("🛟 Life Jackets", 150, 50, "orange"),
            ("🚣 Rescue Boats", 8, 3, "purple"),
        ]
        for name, total, used, _ in resources:
            pct = int((used / total) * 100)
            color = "#ef4444" if pct > 70 else ("#f59e0b" if pct > 40 else "#22c55e")
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; margin-bottom:2px;">'
                f'<span style="color:#cbd5e0; font-size:0.85rem;">{name}</span>'
                f'<span style="color:{color}; font-size:0.85rem;">{used}/{total} deployed ({pct}%)</span></div>',
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

    with col_right:
        st.markdown("### 🚨 Latest Alerts")
        alerts = [
            {"time": "14:35", "msg": "⛈️ Heavy rain warning – Tirunelveli (IMD)", "level": "critical"},
            {"time": "13:20", "msg": "🌊 Thamirabarani river at danger level (Gauge: 14.8m)", "level": "high"},
            {"time": "12:45", "msg": "🏠 Relief camp SH001 at 70% capacity", "level": "moderate"},
            {"time": "11:30", "msg": "🔥 Heat advisory – Madurai & Trichy districts", "level": "moderate"},
            {"time": "10:15", "msg": "✅ NDRF Team 8 deployed to Tenkasi", "level": "info"},
        ]
        for al in alerts:
            cls = f"alert-{al['level']}"
            st.markdown(
                f'<div class="{cls}"><span style="color:#94a3b8; font-size:0.75rem;">{al["time"]}</span><br>'
                f'<span style="font-size:0.85rem;">{al["msg"]}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown("### 🤖 Agent Activity")
        agent_stats = [
            ("Coordinator", "23", "↑"),
            ("Monitoring",  "41", "↑"),
            ("Shelter",     "18", "→"),
            ("Rescue",      "29", "↑"),
            ("Medical",     "12", "→"),
            ("Resource",    "8",  "→"),
        ]
        for agent, calls, trend in agent_stats:
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #1e2533;">'
                f'<span style="color:#94a3b8; font-size:0.8rem;">{agent}</span>'
                f'<span style="color:#60a5fa; font-size:0.85rem;">{calls} calls {trend}</span></div>',
                unsafe_allow_html=True
            )


# ─── PAGE: EMERGENCY ASSISTANT ────────────────────────────────────────────────
def page_emergency_assistant():
    st.markdown("## 🚨 Emergency Assistant")
    st.markdown("*Ask about any disaster situation – our AI agents are ready to help*")

    # Example queries
    st.markdown("**Quick Questions:**")
    example_qs = [
        "What should I do during a flood?",
        "Find the nearest shelter",
        "How to treat heat stroke?",
        "I need rescue – 5 people trapped",
        "Cyclone safety measures",
        "Government flood relief programs",
    ]
    cols = st.columns(3)
    for i, q in enumerate(example_qs):
        if cols[i % 3].button(q, key=f"eq_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            _process_query(q)
            st.rerun()

    st.markdown("---")

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">👤 <strong>You:</strong> {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-assistant">🤖 <strong>RescueMind AI:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )
            if msg.get("explainability"):
                with st.expander("🔍 View Explainability Card"):
                    st.code(msg["explainability"], language=None)

    # Input
    st.markdown("---")
    with st.container():
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Your query",
                placeholder=t("ask_placeholder"),
                label_visibility="collapsed",
                key="chat_input",
            )
        with col_btn:
            send = st.button(t("send"), type="primary", use_container_width=True)

    if send and user_input:
        # Security check
        from security.security_manager import security_manager
        report = security_manager.check_request(user_input, st.session_state.user_id)
        if not report["allowed"]:
            st.error(f"🚫 {'; '.join(report['errors'])}")
        else:
            if report["warnings"]:
                for w in report["warnings"]:
                    st.warning(w)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            _process_query(user_input)
            st.rerun()


def _process_query(query: str):
    """Run the coordinator agent and append response to chat history."""
    with st.spinner("🤖 Agents analyzing your query..."):
        try:
            from agents.coordinator_agent import CoordinatorAgent
            agent = CoordinatorAgent()
            context = {
                "query": query,
                "location": st.session_state.user_location,
                "lat": st.session_state.user_lat,
                "lon": st.session_state.user_lon,
                "session_id": st.session_state.session_id,
                "user_id": st.session_state.user_id,
            }
            result = agent.run(context)
            unified = result.content.get("unified_plan", {})

            # Build rich response
            parts = []
            if unified.get("situation_summary"):
                parts.append(f"**Situation:** {unified['situation_summary']}")
            if unified.get("priority_actions"):
                parts.append("\n**Priority Actions:**")
                for a in unified["priority_actions"][:4]:
                    urgency_emoji = {"immediate": "🔴", "within_1hr": "🟡", "within_24hr": "🟢"}.get(a.get("urgency", ""), "•")
                    parts.append(f"  {urgency_emoji} {a['action']}")
            if unified.get("key_contacts"):
                parts.append(f"\n**Key Contacts:** {' | '.join(unified['key_contacts'][:4])}")
            agents_used = result.content.get("agents_consulted", [])
            if agents_used:
                parts.append(f"\n*Agents consulted: {', '.join(agents_used)}*")

            response_text = "\n".join(parts) if parts else result.recommendation
            if not response_text:
                response_text = "I'm here to help. Please ask about flood safety, shelter locations, rescue assistance, or emergency medical guidance."

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_text,
                "explainability": result.to_explainability_card(),
            })
        except Exception as e:
            logger.error(f"Query processing error: {e}", exc_info=True)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": (
                    "I'm your emergency assistant. During disasters:\n"
                    "• **Emergency**: Call **112**\n"
                    "• **Ambulance**: Call **108**\n"
                    "• **Flood Help**: Call **1077**\n"
                    "• **Disaster Control**: Call **1079**\n\n"
                    "Please also refer to official NDMA guidelines at ndma.gov.in"
                ),
            })


# ─── PAGE: DISASTER MONITORING ────────────────────────────────────────────────
def page_monitoring():
    st.markdown("## 🌊 Disaster Monitoring")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📡 Active Threat Assessment")
        with st.container():
            st.markdown("""
<div class="alert-critical">
<strong>⚠️ ACTIVE FLOOD WATCH – TIRUNELVELI</strong><br>
Thamirabarani River: <strong>14.8m / Danger Level: 14.5m</strong><br>
Issued by: TN SDMA | Valid until: 24 June 2026 06:00 IST
</div>""", unsafe_allow_html=True)
            st.markdown("""
<div class="alert-moderate">
<strong>🔥 HEAT WAVE WARNING – INTERIOR TAMIL NADU</strong><br>
Max temp: <strong>42°C+</strong> in Madurai, Trichy, Salem | IMD Orange Alert<br>
Issued by: IMD | Valid until: 23 June 2026 12:00 IST
</div>""", unsafe_allow_html=True)

        st.markdown("### 🗓️ Event Timeline (Last 48 Hours)")
        timeline_events = [
            ("2026-06-22 14:00", "🔴", "Flood Level CRITICAL – Thamirabarani dam discharge increased to 1.2 lakh cusecs"),
            ("2026-06-22 10:30", "🟡", "SDRF team deployed to Papanasam and Nanguneri taluks"),
            ("2026-06-22 06:00", "🟡", "IMD Heavy Rainfall Warning extended for 24 hours"),
            ("2026-06-21 22:00", "🔴", "Thamirabarani river crosses danger level at Tirunelveli gauge"),
            ("2026-06-21 16:45", "🟢", "NDRF Team 8 arrived from Chennai at Tirunelveli"),
            ("2026-06-21 12:00", "🟡", "Advisory issued for Kanyakumari coastal areas"),
            ("2026-06-21 08:00", "🟢", "Pre-emptive shelter camps opened at 6 locations"),
            ("2026-06-20 20:00", "🟡", "Cyclone Mandous remnant bringing heavy rain to TN coast"),
        ]
        for ts, emoji, event in timeline_events:
            st.markdown(
                f'<div style="display:flex; gap:12px; padding:6px 0; border-bottom:1px solid #1e2533;">'
                f'<span style="color:#94a3b8; font-size:0.75rem; min-width:130px;">{ts}</span>'
                f'<span>{emoji}</span>'
                f'<span style="color:#cbd5e0; font-size:0.85rem;">{event}</span></div>',
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("### 🌡️ Current Weather")
        st.markdown("""
<div class="card">
<div style="font-size:1.1rem; font-weight:700; color:#e2e8f0;">Tirunelveli</div>
<div style="font-size:2.5rem; color:#60a5fa;">🌧️ 29.8°C</div>
<div style="color:#94a3b8; font-size:0.85rem;">Heavy Rain | Humidity: 92%</div>
<hr style="border-color:#2d3748; margin:0.5rem 0;">
<div style="display:flex; justify-content:space-between; font-size:0.8rem;">
<span style="color:#94a3b8;">💨 Wind</span><span style="color:#cbd5e0;">12 m/s</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.8rem;">
<span style="color:#94a3b8;">🌧️ Rain/hr</span><span style="color:#ef4444; font-weight:700;">42.5 mm</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.8rem;">
<span style="color:#94a3b8;">📊 Pressure</span><span style="color:#cbd5e0;">998 hPa</span>
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("### 📊 Risk Levels by District")
        districts = [
            ("Tirunelveli", 4, "🔴"),
            ("Tenkasi", 3, "🟠"),
            ("Kanyakumari", 3, "🟠"),
            ("Madurai", 2, "🟡"),
            ("Trichy", 2, "🟡"),
            ("Chennai", 2, "🟡"),
            ("Coimbatore", 1, "🟢"),
            ("Salem", 1, "🟢"),
        ]
        for dist, level, emoji in districts:
            bar_color = ["#22c55e","#22c55e","#f59e0b","#f97316","#ef4444"][level-1]
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin:4px 0;">'
                f'<span style="color:#cbd5e0; font-size:0.85rem; width:120px;">{emoji} {dist}</span>'
                f'<div style="flex:1; background:#2d3748; border-radius:4px; height:8px; margin:0 8px;">'
                f'<div style="background:{bar_color}; width:{level*20}%; height:8px; border-radius:4px;"></div>'
                f'</div><span style="color:{bar_color}; font-size:0.8rem; font-weight:700;">L{level}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown("### 📱 Quick Alert")
        disaster = st.selectbox("Disaster Type", ["flood","cyclone","earthquake","heatwave"], key="alert_type")
        sev = st.slider("Severity", 1, 5, 3, key="alert_sev")
        if st.button("🚨 Generate Alert", type="primary", use_container_width=True):
            from agents.alert_agent import EmergencyAlertAgent
            agent = EmergencyAlertAgent()
            result = agent.run({
                "disaster_type": disaster, "location": st.session_state.user_location,
                "severity": sev, "language": st.session_state.language,
            })
            alert = result.content.get("alert", {})
            lang = st.session_state.language
            msg = alert.get(f"message_{lang}", alert.get("message_en", result.recommendation))
            st.success(f"**{alert.get('title','Alert')}**\n\n{msg}")


# ─── PAGE: SHELTER FINDER ─────────────────────────────────────────────────────
def page_shelter_finder():
    st.markdown("## 🏠 Shelter Finder")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📍 Your Location")
        location_input = st.text_input("Location", value=st.session_state.user_location, key="loc_input")
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Latitude", value=st.session_state.user_lat, format="%.4f")
        lon = col_lon.number_input("Longitude", value=st.session_state.user_lon, format="%.4f")
        disaster_type = st.selectbox("Disaster Type", ["flood","cyclone","earthquake","general"], key="sh_dtype")

        if st.button("🔍 Find Shelters", type="primary", use_container_width=True):
            st.session_state.user_location = location_input
            st.session_state.user_lat = lat
            st.session_state.user_lon = lon
            from agents.shelter_agent import ShelterEvacuationAgent
            agent = ShelterEvacuationAgent()
            result = agent.run({
                "lat": lat, "lon": lon,
                "disaster_type": disaster_type,
                "location": location_input,
            })
            st.session_state["shelter_results"] = result

    with col2:
        st.markdown("### 🏠 Available Shelters")
        result = st.session_state.get("shelter_results")
        if result:
            shelters = result.content.get("shelters", [])
            for i, sh in enumerate(shelters):
                facilities = json.loads(sh.get("facilities") or "[]")
                cap = sh.get("capacity", 0)
                occ = sh.get("current_occupancy", 0)
                avail = cap - occ
                pct = round((occ / max(cap, 1)) * 100)
                occ_color = "#ef4444" if pct > 80 else ("#f59e0b" if pct > 60 else "#22c55e")
                rank_badge = ["🥇","🥈","🥉","4️⃣","5️⃣"][i] if i < 5 else f"{i+1}"

                st.markdown(f"""
<div class="shelter-card">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <span style="font-size:1rem; font-weight:700; color:#e2e8f0;">{rank_badge} {sh.get('name','Shelter')}</span><br>
      <span style="font-size:0.8rem; color:#94a3b8;">📍 {sh.get('address','')} | 📏 {sh.get('distance_km',0)} km away</span>
    </div>
    <div style="text-align:right;">
      <div style="color:{occ_color}; font-weight:700; font-size:0.9rem;">{avail} available</div>
      <div style="font-size:0.75rem; color:#94a3b8;">{occ}/{cap} occupied ({pct}%)</div>
    </div>
  </div>
  <div style="margin-top:0.5rem; display:flex; gap:6px; flex-wrap:wrap;">
    {''.join([f'<span style="background:#1e3a5f; color:#60a5fa; border-radius:4px; padding:2px 6px; font-size:0.75rem;">{f}</span>' for f in facilities[:5]])}
  </div>
  <div style="margin-top:0.5rem;">
    <span style="color:#94a3b8; font-size:0.8rem;">📞 {sh.get('contact_phone','N/A')}</span>
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.info("Enter your location above and click **Find Shelters** to see nearby relief camps.")
            # Show demo shelters
            from agents.shelter_agent import ShelterEvacuationAgent
            agent = ShelterEvacuationAgent()
            result = agent.run({"lat": 8.7139, "lon": 77.7567, "disaster_type": "flood", "location": "Tirunelveli"})
            st.session_state["shelter_results"] = result
            st.rerun()


# ─── PAGE: RESOURCE CENTER ────────────────────────────────────────────────────
def page_resources():
    st.markdown("## 📦 Resource Center")

    from agents.resource_agent import ResourceAllocationAgent
    agent = ResourceAllocationAgent()
    result = agent.run({
        "disaster_type": "flood", "num_people": 5000,
        "location": st.session_state.user_location,
    })
    content = result.content

    c1, c2, c3 = st.columns(3)
    resources_summary = [
        ("🍱 Food", "5,000", "packets", "72%", "#f59e0b"),
        ("💧 Water", "1,200", "cans 20L", "45%", "#22c55e"),
        ("💊 Medicine", "300", "kits", "38%", "#22c55e"),
        ("🛟 Jackets", "150", "units", "67%", "#f97316"),
        ("🚣 Boats", "8", "units", "88%", "#ef4444"),
        ("⛺ Tents", "500", "units", "25%", "#22c55e"),
    ]
    cols = st.columns(3)
    for i, (name, qty, unit, pct, color) in enumerate(resources_summary):
        with cols[i % 3]:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">{name}</div>
<div class="metric-value" style="color:{color};">{qty}</div>
<div style="color:#94a3b8; font-size:0.8rem;">{unit} available | {pct} deployed</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### 📊 Supply vs Demand Analysis")
        reqs = content.get("requirements", {})
        avails = content.get("availability", {})
        for item, req_key, avail_key in [
            ("Food Packets", "food_packets", "food_packets"),
            ("Water Cans (20L)", "water_cans", "water_cans"),
            ("First Aid Kits", "first_aid_kits", "first_aid_kits"),
        ]:
            req = reqs.get(req_key, 0)
            avail = avails.get(avail_key, 0)
            pct = min(int((avail / max(req, 1)) * 100), 100)
            color = "#22c55e" if pct >= 80 else ("#f59e0b" if pct >= 50 else "#ef4444")
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; margin-bottom:3px;">'
                f'<span style="color:#cbd5e0; font-size:0.85rem;">{item}</span>'
                f'<span style="color:{color}; font-size:0.85rem;">{avail}/{req} ({pct}%)</span></div>',
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

        gaps = content.get("supply_gaps", [])
        if gaps:
            st.markdown("**⚠️ Supply Gaps Detected:**")
            for g in gaps:
                st.markdown(f'<div class="alert-high">⚠️ {g}</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("### 📍 Distribution Points")
        depots = [
            {"name": "Tirunelveli Main Warehouse", "lat": 8.7139, "lon": 77.7567, "status": "Active",
             "stock": "Full", "contact": "0462-2334567"},
            {"name": "Medical Supply Store – Palayamkottai", "lat": 8.7234, "lon": 77.7401, "status": "Active",
             "stock": "Partial", "contact": "0462-2335678"},
            {"name": "Fire Station – Emergency Depot", "lat": 8.7100, "lon": 77.7500, "status": "Active",
             "stock": "Low", "contact": "0462-2334999"},
        ]
        for dep in depots:
            stk_color = {"Full": "#22c55e", "Partial": "#f59e0b", "Low": "#ef4444"}.get(dep["stock"], "#94a3b8")
            st.markdown(f"""
<div class="card">
  <strong style="color:#e2e8f0;">{dep['name']}</strong><br>
  <span style="color:{stk_color}; font-size:0.85rem;">● {dep['stock']} Stock</span>
  <span style="color:#94a3b8; font-size:0.8rem;"> | {dep['contact']}</span>
</div>""", unsafe_allow_html=True)


# ─── PAGE: RELIEF PROGRAMS ────────────────────────────────────────────────────
def page_relief():
    st.markdown("## 💰 Government Relief Programs")

    from agents.relief_agent import GovernmentReliefAgent
    agent = GovernmentReliefAgent()
    result = agent.run({"disaster_type": "flood", "state": "Tamil Nadu"})
    programs = result.content.get("programs", [])

    st.markdown(f"*{len(programs)} programs found for flood victims in Tamil Nadu*")

    filter_type = st.selectbox("Filter by Provider", ["All", "Central Government", "Tamil Nadu State Government", "NGO"])

    for prog in programs:
        if filter_type != "All" and prog.get("provider") != filter_type:
            continue
        provider_color = {
            "Central Government": "#3b82f6",
            "Tamil Nadu State Government": "#22c55e",
            "NGO": "#f59e0b",
            "NGO/International": "#a855f7",
        }.get(prog.get("provider", ""), "#94a3b8")

        st.markdown(f"""
<div class="card" style="border-left: 4px solid {provider_color}; margin-bottom:1rem;">
  <div style="display:flex; justify-content:space-between; align-items:start; flex-wrap:wrap;">
    <div style="flex:1;">
      <div style="font-size:1rem; font-weight:700; color:#e2e8f0;">{prog.get('name','Program')}</div>
      <div style="font-size:0.8rem; color:{provider_color}; margin:2px 0;">{prog.get('provider','')}</div>
      <div style="font-size:0.85rem; color:#94a3b8; margin-top:4px;">{prog.get('description','')[:150]}...</div>
    </div>
  </div>
  <hr style="border-color:#2d3748; margin:0.6rem 0;">
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
    <div><div style="color:#94a3b8; font-size:0.75rem;">💰 Benefits</div>
    <div style="color:#22c55e; font-size:0.82rem;">{prog.get('benefits','')[:100]}</div></div>
    <div><div style="color:#94a3b8; font-size:0.75rem;">✅ Eligibility</div>
    <div style="color:#cbd5e0; font-size:0.82rem;">{prog.get('eligibility','')[:100]}</div></div>
    <div><div style="color:#94a3b8; font-size:0.75rem;">📞 Contact</div>
    <div style="color:#60a5fa; font-size:0.82rem; font-weight:700;">{prog.get('contact_info','N/A')}</div></div>
    <div><div style="color:#94a3b8; font-size:0.75rem;">🔗 Apply</div>
    <div style="font-size:0.82rem;"><a href="{prog.get('application_url','#')}" style="color:#60a5fa;">{prog.get('application_url','N/A')[:40]}</a></div></div>
  </div>
</div>""", unsafe_allow_html=True)


# ─── PAGE: SETTINGS ───────────────────────────────────────────────────────────
def page_settings():
    st.markdown("## ⚙️ Settings & Profile")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 User Profile")
        st.text_input("Display Name", value="Anonymous User", key="s_name")
        st.selectbox("Role", ["Citizen","Emergency Responder","NGO Worker","Government Official"], key="s_role")
        st.text_input("Location", value=st.session_state.user_location, key="s_loc")
        st.text_input("Phone (optional)", placeholder="For emergency callback", key="s_phone")

        st.markdown("### 🌐 Language")
        lang_choice = st.radio("Preferred Language", ["English","தமிழ் (Tamil)","हिंदी (Hindi)"], key="s_lang")
        lang_map = {"English":"en","தமிழ் (Tamil)":"ta","हिंदी (Hindi)":"hi"}
        if st.button("💾 Save Settings", type="primary"):
            st.session_state.language = lang_map.get(lang_choice,"en")
            st.success("✅ Settings saved!")

    with col2:
        st.markdown("### 🔔 Alert Preferences")
        st.checkbox("Flood warnings", value=True, key="pref_flood")
        st.checkbox("Cyclone warnings", value=True, key="pref_cyclone")
        st.checkbox("Earthquake alerts", value=True, key="pref_earthquake")
        st.checkbox("Heat wave advisories", value=True, key="pref_heat")
        st.checkbox("Government relief notifications", value=False, key="pref_relief")

        st.markdown("### 🔒 Security & Privacy")
        st.info("✅ Your data is stored locally and never shared without consent.")
        st.info("✅ All inputs are validated and PII is automatically redacted.")
        st.info("✅ Session ID: " + st.session_state.session_id)

        st.markdown("### 🤖 About RescueMind AI")
        st.markdown("""
<div class="card">
<strong style="color:#e2e8f0;">RescueMind AI v1.0</strong><br>
<span style="color:#94a3b8; font-size:0.85rem;">Multi-Agent Disaster Response System</span><br><br>
<div style="font-size:0.82rem; color:#94a3b8;">
Agents: 10 specialized AI agents<br>
MCP Servers: 6 data sources<br>
Languages: English, Tamil, Hindi<br>
Model: Google Gemini 1.5 Pro/Flash<br>
Database: SQLite<br>
Framework: Streamlit + LangChain concepts<br>
</div>
</div>""", unsafe_allow_html=True)


# ─── Main App Router ──────────────────────────────────────────────────────────
def main():
    inject_css()
    init_session()
    render_sidebar()

    page = st.session_state.current_page
    if   page == "Dashboard":             page_dashboard()
    elif page == "Emergency Assistant":   page_emergency_assistant()
    elif page == "Disaster Monitoring":   page_monitoring()
    elif page == "Shelter Finder":        page_shelter_finder()
    elif page == "Resource Center":       page_resources()
    elif page == "Relief Programs":       page_relief()
    elif page == "Settings":              page_settings()
    else:                                 page_dashboard()


if __name__ == "__main__":
    main()
