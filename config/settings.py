"""
RescueMind AI – Configuration & Settings
Central configuration management for all agents, services, and deployment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── Base Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"

# Create dirs if they don't exist
for d in [DATA_DIR, DB_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

# ─── API Keys ─────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
RELIEFWEB_API_KEY = os.getenv("RELIEFWEB_API_KEY", "")

# ─── Gemini Model Config ───────────────────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))   # Low for factual disaster info

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/rescuemind.db")
DATABASE_PATH = str(DB_DIR / "rescuemind.db")

# ─── MCP Server Ports ─────────────────────────────────────────────────────────
MCP_WEATHER_PORT = int(os.getenv("MCP_WEATHER_PORT", "8001"))
MCP_SHELTER_PORT = int(os.getenv("MCP_SHELTER_PORT", "8002"))
MCP_RESOURCE_PORT = int(os.getenv("MCP_RESOURCE_PORT", "8003"))
MCP_RELIEF_PORT = int(os.getenv("MCP_RELIEF_PORT", "8004"))
MCP_MEDICAL_PORT = int(os.getenv("MCP_MEDICAL_PORT", "8005"))
MCP_CONTACT_PORT = int(os.getenv("MCP_CONTACT_PORT", "8006"))

# ─── Security ─────────────────────────────────────────────────────────────────
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))   # per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))        # seconds
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "2000"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# ─── Supported Languages ──────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
}
DEFAULT_LANGUAGE = "en"

# ─── Disaster Severity Levels ─────────────────────────────────────────────────
SEVERITY_LEVELS = {
    1: {"label": "Low",      "color": "#22c55e", "action": "Monitor"},
    2: {"label": "Moderate", "color": "#f59e0b", "action": "Prepare"},
    3: {"label": "High",     "color": "#f97316", "action": "Alert"},
    4: {"label": "Critical", "color": "#ef4444", "action": "Evacuate"},
    5: {"label": "Extreme",  "color": "#7c3aed", "action": "Emergency"},
}

# ─── Disaster Types ───────────────────────────────────────────────────────────
DISASTER_TYPES = [
    "flood", "cyclone", "earthquake", "wildfire",
    "landslide", "tsunami", "storm", "drought", "heatwave", "industrial",
]

# ─── Agent Names ──────────────────────────────────────────────────────────────
AGENTS = {
    "coordinator":   "Coordinator Agent",
    "monitoring":    "Disaster Monitoring Agent",
    "alert":         "Emergency Alert Agent",
    "shelter":       "Shelter & Evacuation Agent",
    "rescue":        "Rescue Coordination Agent",
    "medical":       "Medical Assistance Agent",
    "resource":      "Resource Allocation Agent",
    "damage":        "Damage Assessment Agent",
    "relief":        "Government Relief Agent",
    "planning":      "Planning Agent",
}

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = str(LOG_DIR / "rescuemind.log")

# ─── Demo Mode (uses mock data when APIs unavailable) ─────────────────────────
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# ─── App Metadata ─────────────────────────────────────────────────────────────
APP_NAME = "RescueMind AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Multi-Agent Disaster Response & Emergency Coordination System"
APP_AUTHOR = "RescueMind Team"
