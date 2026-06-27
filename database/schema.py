"""
RescueMind AI – Database Schema & Initialization
SQLite database with all tables for disaster response data.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)


# ─── Schema SQL ───────────────────────────────────────────────────────────────
SCHEMA_SQL = """

-- Users table: citizens, responders, NGOs, government agencies
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT UNIQUE NOT NULL,
    name            TEXT,
    role            TEXT DEFAULT 'citizen',      -- citizen|responder|ngo|government
    language        TEXT DEFAULT 'en',
    location_lat    REAL,
    location_lon    REAL,
    location_name   TEXT,
    phone           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    last_active     TEXT DEFAULT (datetime('now')),
    is_active       INTEGER DEFAULT 1
);

-- Disaster Events: tracked and verified disaster occurrences
CREATE TABLE IF NOT EXISTS disaster_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id        TEXT UNIQUE NOT NULL,
    disaster_type   TEXT NOT NULL,               -- flood|cyclone|earthquake|etc.
    title           TEXT NOT NULL,
    description     TEXT,
    severity        INTEGER DEFAULT 1,           -- 1(Low) to 5(Extreme)
    status          TEXT DEFAULT 'active',       -- active|monitoring|resolved
    location_name   TEXT,
    location_lat    REAL,
    location_lon    REAL,
    affected_area   TEXT,
    source          TEXT,                        -- data source (API/manual/alert)
    source_url      TEXT,
    started_at      TEXT,
    ended_at        TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- Shelter Data: evacuation shelters and safe zones
CREATE TABLE IF NOT EXISTS shelters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shelter_id      TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    address         TEXT,
    location_lat    REAL,
    location_lon    REAL,
    district        TEXT,
    state           TEXT,
    capacity        INTEGER DEFAULT 0,
    current_occupancy INTEGER DEFAULT 0,
    shelter_type    TEXT DEFAULT 'general',      -- general|medical|pet-friendly|etc.
    facilities      TEXT,                        -- JSON array of facilities
    contact_phone   TEXT,
    contact_name    TEXT,
    is_active       INTEGER DEFAULT 1,
    disaster_types  TEXT,                        -- JSON array of applicable disaster types
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- Emergency Requests: rescue and help requests
CREATE TABLE IF NOT EXISTS emergency_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id      TEXT UNIQUE NOT NULL,
    user_id         TEXT,
    request_type    TEXT NOT NULL,               -- rescue|medical|evacuation|resource
    description     TEXT NOT NULL,
    severity        INTEGER DEFAULT 3,
    priority_score  REAL DEFAULT 0.0,
    status          TEXT DEFAULT 'pending',      -- pending|assigned|in_progress|resolved
    location_lat    REAL,
    location_lon    REAL,
    location_name   TEXT,
    num_people      INTEGER DEFAULT 1,
    has_injured     INTEGER DEFAULT 0,
    has_children    INTEGER DEFAULT 0,
    has_elderly     INTEGER DEFAULT 0,
    assigned_team   TEXT,
    response_notes  TEXT,
    disaster_event_id TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    resolved_at     TEXT
);

-- Resource Inventory: supplies and equipment tracking
CREATE TABLE IF NOT EXISTS resource_inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id     TEXT UNIQUE NOT NULL,
    resource_type   TEXT NOT NULL,               -- food|water|medicine|equipment|shelter_kit
    name            TEXT NOT NULL,
    quantity        REAL DEFAULT 0,
    unit            TEXT DEFAULT 'units',
    location_name   TEXT,
    location_lat    REAL,
    location_lon    REAL,
    available       INTEGER DEFAULT 1,
    last_updated    TEXT DEFAULT (datetime('now')),
    expiry_date     TEXT,
    notes           TEXT
);

-- Medical Requests: medical assistance tracking
CREATE TABLE IF NOT EXISTS medical_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id      TEXT UNIQUE NOT NULL,
    user_id         TEXT,
    symptoms        TEXT,
    condition_type  TEXT,                        -- injury|illness|trauma|chronic
    severity        INTEGER DEFAULT 1,
    location_name   TEXT,
    location_lat    REAL,
    location_lon    REAL,
    num_patients    INTEGER DEFAULT 1,
    ai_guidance     TEXT,                        -- AI-generated first aid guidance
    hospital_ref    TEXT,                        -- Recommended hospital
    status          TEXT DEFAULT 'pending',
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- Government Relief Programs: relief schemes and eligibility
CREATE TABLE IF NOT EXISTS relief_programs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id      TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    provider        TEXT,                        -- Central Gov|State Gov|NGO
    disaster_types  TEXT,                        -- JSON array
    eligibility     TEXT,
    benefits        TEXT,
    application_url TEXT,
    contact_info    TEXT,
    state           TEXT,                        -- State-specific or 'national'
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Relief Applications: user applications for government relief
CREATE TABLE IF NOT EXISTS relief_applications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  TEXT UNIQUE NOT NULL,
    user_id         TEXT,
    program_id      TEXT,
    disaster_event_id TEXT,
    applicant_name  TEXT,
    applicant_phone TEXT,
    details         TEXT,                        -- Application details JSON
    status          TEXT DEFAULT 'submitted',    -- submitted|under_review|approved|rejected
    submission_date TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    notes           TEXT
);

-- Agent Logs: all agent invocations for audit and analysis
CREATE TABLE IF NOT EXISTS agent_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id          TEXT UNIQUE NOT NULL,
    agent_name      TEXT NOT NULL,
    action          TEXT NOT NULL,
    input_summary   TEXT,
    output_summary  TEXT,
    confidence      REAL,
    duration_ms     INTEGER,
    status          TEXT DEFAULT 'success',      -- success|error|timeout
    user_id         TEXT,
    session_id      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Advisory History: past AI recommendations and outcomes
CREATE TABLE IF NOT EXISTS advisory_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    advisory_id     TEXT UNIQUE NOT NULL,
    user_id         TEXT,
    session_id      TEXT,
    query           TEXT,
    advisory_type   TEXT,                        -- evacuation|medical|resource|general
    recommendation  TEXT,
    confidence      REAL,
    data_sources    TEXT,                        -- JSON array of sources used
    risk_level      TEXT,
    alternatives    TEXT,                        -- JSON array of alternatives
    was_helpful     INTEGER,                     -- 1=yes, 0=no, NULL=unrated
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Alert History: generated emergency alerts
CREATE TABLE IF NOT EXISTS alert_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id        TEXT UNIQUE NOT NULL,
    disaster_event_id TEXT,
    alert_type      TEXT NOT NULL,               -- warning|watch|advisory|emergency
    title           TEXT NOT NULL,
    message         TEXT NOT NULL,
    severity        INTEGER,
    target_area     TEXT,
    target_roles    TEXT,                        -- JSON array: citizen|responder|etc.
    languages       TEXT,                        -- JSON array of languages
    issued_by       TEXT DEFAULT 'RescueMind AI',
    is_active       INTEGER DEFAULT 1,
    expires_at      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ─── Indexes for Performance ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_disaster_events_type    ON disaster_events(disaster_type);
CREATE INDEX IF NOT EXISTS idx_disaster_events_status  ON disaster_events(status);
CREATE INDEX IF NOT EXISTS idx_emergency_requests_status ON emergency_requests(status);
CREATE INDEX IF NOT EXISTS idx_emergency_requests_severity ON emergency_requests(severity);
CREATE INDEX IF NOT EXISTS idx_shelters_district       ON shelters(district);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent        ON agent_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_advisory_history_user   ON advisory_history(user_id);
"""


# ─── Seed Data ────────────────────────────────────────────────────────────────
SEED_SHELTERS = [
    ("SH001", "District Collector Office Relief Camp", "Tirunelveli Main Road", 8.7139, 77.7567,
     "Tirunelveli", "Tamil Nadu", 500, 120, "general", '["water","food","toilet","medical_aid"]',
     "0462-2334567", "District Collector", 1, '["flood","cyclone","earthquake"]'),
    ("SH002", "Nellai Govt High School Shelter", "Palayamkottai", 8.7234, 77.7401,
     "Tirunelveli", "Tamil Nadu", 300, 85, "general", '["water","food","toilet"]',
     "0462-2335678", "School Principal", 1, '["flood","cyclone"]'),
    ("SH003", "YMCA Community Hall", "Melapalayam", 8.7051, 77.7389,
     "Tirunelveli", "Tamil Nadu", 200, 40, "general", '["water","food","generator"]',
     "9876543210", "YMCA Manager", 1, '["flood","storm"]'),
    ("SH004", "Chennai Rajaji Hall Relief Center", "Anna Salai, Chennai", 13.0569, 80.2520,
     "Chennai", "Tamil Nadu", 2000, 450, "general", '["water","food","toilet","medical_aid","wifi"]',
     "044-25671234", "Relief Coordinator", 1, '["flood","cyclone","tsunami"]'),
    ("SH005", "Madurai Medical College Emergency Camp", "Panagal Road, Madurai", 9.9192, 78.1192,
     "Madurai", "Tamil Nadu", 400, 90, "medical", '["water","food","doctors","ambulance","medicine"]',
     "0452-2534567", "Medical Officer", 1, '["earthquake","industrial","general"]'),
    ("SH006", "Coimbatore CODISSIA Trade Fair Ground", "Avinashi Road, Coimbatore", 11.0168, 76.9558,
     "Coimbatore", "Tamil Nadu", 3000, 200, "general", '["water","food","toilet","generator","parking"]',
     "0422-4217777", "Event Manager", 1, '["flood","earthquake","fire"]'),
]

SEED_RESOURCES = [
    ("RES001", "food", "Ready-to-Eat Meal Packets", 5000, "packets", "Tirunelveli Warehouse", 8.7139, 77.7567),
    ("RES002", "water", "Drinking Water Cans (20L)", 1200, "cans",   "Tirunelveli Warehouse", 8.7139, 77.7567),
    ("RES003", "medicine", "First Aid Kits",            300, "kits",    "Medical Store – Tirunelveli", 8.7200, 77.7600),
    ("RES004", "medicine", "Oral Rehydration Salts",   2000, "packets", "Medical Store – Tirunelveli", 8.7200, 77.7600),
    ("RES005", "equipment","Life Jackets",              150, "units",   "Fire Station – Tirunelveli", 8.7100, 77.7500),
    ("RES006", "equipment","Rescue Boats",               8,  "units",   "Fire Station – Tirunelveli", 8.7100, 77.7500),
    ("RES007", "food", "Rice Bags (25kg)",            2000, "bags",    "Chennai State Warehouse", 13.0569, 80.2520),
    ("RES008", "water", "Water Purification Tablets", 10000,"tablets", "Chennai State Warehouse", 13.0569, 80.2520),
    ("RES009", "equipment","Tents (8-person)",           500, "units",  "Disaster Relief Depot – Chennai", 13.0600, 80.2600),
    ("RES010", "medicine", "Snake Anti-Venom",          100, "vials",  "Madurai Medical College", 9.9192, 78.1192),
]

SEED_RELIEF_PROGRAMS = [
    ("RP001", "PM Fasal Bima Yojana – Crop Loss",
     "Compensation for farmers affected by natural calamities affecting crops.",
     "Central Government", '["flood","drought","cyclone","hailstorm"]',
     "Farmer with Kisan Credit Card; crop loss > 50%",
     "Up to ₹2 lakhs crop insurance payout",
     "https://pmfby.gov.in", "1800-180-1551", "national"),
    ("RP002", "Tamil Nadu CM Relief Fund – Natural Disaster",
     "Immediate financial assistance to disaster-affected families in Tamil Nadu.",
     "Tamil Nadu State Government", '["flood","cyclone","earthquake","fire"]',
     "Resident of Tamil Nadu; affected by notified disaster",
     "₹5,000–25,000 immediate relief; up to ₹1 lakh for house damage",
     "https://tnlive.tn.gov.in", "0044-25671234", "Tamil Nadu"),
    ("RP003", "National Disaster Response Fund (NDRF)",
     "Central assistance for states severely affected by disasters.",
     "Central Government", '["flood","earthquake","cyclone","landslide","tsunami"]',
     "State government application; declared disaster zone",
     "Infrastructure rebuilding; relief supplies; housing grants",
     "https://ndma.gov.in", "011-26701700", "national"),
    ("RP004", "Pradhan Mantri Awas Yojana – Disaster Housing",
     "Reconstruction of houses damaged or destroyed in disasters.",
     "Central Government", '["flood","earthquake","cyclone","fire"]',
     "BPL family; house damaged > 50%; no prior PMAY benefit",
     "₹1.2–1.5 lakhs for rural; ₹2.5 lakhs for urban housing reconstruction",
     "https://pmaymis.gov.in", "1800-11-6163", "national"),
    ("RP005", "UNDP – India Disaster Risk Reduction",
     "International support for communities in high-risk disaster zones.",
     "NGO/International", '["flood","drought","cyclone","earthquake"]',
     "Marginalized communities in disaster-prone districts",
     "Training, early warning systems, community resilience building",
     "https://undp.org/india", "011-46532333", "national"),
    ("RP006", "Red Cross Emergency Relief – Tamil Nadu",
     "Immediate relief: food, water, shelter kits for disaster victims.",
     "NGO", '["flood","cyclone","fire","earthquake"]',
     "Any disaster-affected individual",
     "Food packets, hygiene kits, temporary shelter, blankets",
     "https://redcross.in", "1800-111-110", "Tamil Nadu"),
]

SEED_DISASTER_EVENTS = [
    ("DE001", "flood",     "Thamirabarani River Flooding",
     "Heavy rainfall causing Thamirabarani River to overflow affecting low-lying areas.",
     3, "active", "Tirunelveli, Tamil Nadu", 8.7139, 77.7567,
     "Tirunelveli, Tenkasi, Kanyakumari districts"),
    ("DE002", "cyclone",   "Cyclone Mandous (Historical Reference)",
     "Historical cyclone event used as reference for training and simulation.",
     4, "resolved", "Chennai Coast, Tamil Nadu", 13.0569, 80.2520,
     "Chennai, Villupuram, Cuddalore"),
    ("DE003", "heatwave",  "Severe Heatwave – Interior Tamil Nadu",
     "Temperature exceeding 42°C in interior districts; heat stroke risk high.",
     2, "monitoring", "Madurai, Trichy, Salem", 10.3225, 78.2168,
     "Madurai, Trichy, Salem, Dharmapuri"),
]


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # Better concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize_database(force_reset: bool = False) -> None:
    """
    Create all tables and seed initial data.
    
    Args:
        force_reset: If True, drops and recreates all tables (use with caution).
    """
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    conn = get_connection()
    try:
        if force_reset:
            logger.warning("Force reset: dropping existing tables!")
            _drop_all_tables(conn)

        # Create all tables
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        logger.info("Schema created successfully.")

        # Seed data
        _seed_shelters(conn)
        _seed_resources(conn)
        _seed_relief_programs(conn)
        _seed_disaster_events(conn)
        conn.commit()
        logger.info("Database seeded successfully.")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def _drop_all_tables(conn: sqlite3.Connection) -> None:
    tables = [
        "users", "disaster_events", "shelters", "emergency_requests",
        "resource_inventory", "medical_requests", "relief_programs",
        "relief_applications", "agent_logs", "advisory_history", "alert_history",
    ]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")


def _seed_shelters(conn: sqlite3.Connection) -> None:
    sql = """INSERT OR IGNORE INTO shelters
             (shelter_id, name, address, location_lat, location_lon,
              district, state, capacity, current_occupancy, shelter_type,
              facilities, contact_phone, contact_name, is_active, disaster_types)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, SEED_SHELTERS)
    logger.info(f"Seeded {len(SEED_SHELTERS)} shelters.")


def _seed_resources(conn: sqlite3.Connection) -> None:
    sql = """INSERT OR IGNORE INTO resource_inventory
             (resource_id, resource_type, name, quantity, unit,
              location_name, location_lat, location_lon)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, SEED_RESOURCES)
    logger.info(f"Seeded {len(SEED_RESOURCES)} resources.")


def _seed_relief_programs(conn: sqlite3.Connection) -> None:
    sql = """INSERT OR IGNORE INTO relief_programs
             (program_id, name, description, provider, disaster_types,
              eligibility, benefits, application_url, contact_info, state)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, SEED_RELIEF_PROGRAMS)
    logger.info(f"Seeded {len(SEED_RELIEF_PROGRAMS)} relief programs.")


def _seed_disaster_events(conn: sqlite3.Connection) -> None:
    sql = """INSERT OR IGNORE INTO disaster_events
             (event_id, disaster_type, title, description, severity, status,
              location_name, location_lat, location_lon, affected_area)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, SEED_DISASTER_EVENTS)
    logger.info(f"Seeded {len(SEED_DISASTER_EVENTS)} disaster events.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_database()
    print("✅ Database initialized successfully!")
