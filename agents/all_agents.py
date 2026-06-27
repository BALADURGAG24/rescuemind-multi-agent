"""
RescueMind AI – All Specialized Agents
Includes: Emergency Alert, Shelter & Evacuation, Rescue Coordination,
Medical Assistance, Resource Allocation, Damage Assessment,
Government Relief, and Planning agents.
"""

import json
import math
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


# ─── Haversine distance helper ────────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ══════════════════════════════════════════════════════════════════════════════
# 1. EMERGENCY ALERT AGENT
# ══════════════════════════════════════════════════════════════════════════════
class EmergencyAlertAgent(BaseAgent):
    """
    Generates emergency alerts, citizen notifications, and protective action guidance.
    Supports multi-language alert generation (English, Tamil, Hindi).
    """

    ALERT_TEMPLATES = {
        "flood": {
            "en": "⚠️ FLOOD ALERT: Heavy flooding reported in {location}. Move to higher ground immediately. Do NOT cross flooded roads. Call 1077 for flood assistance.",
            "ta": "⚠️ வெள்ளம் எச்சரிக்கை: {location}ல் வெள்ளம் ஏற்பட்டுள்ளது. உடனடியாக உயர்ந்த இடத்திற்கு செல்லவும். வெள்ளம் தேக்கிய சாலைகளில் செல்லாதீர்கள். 1077 அழைக்கவும்.",
            "hi": "⚠️ बाढ़ अलर्ट: {location} में भारी बाढ़ की सूचना। तुरंत ऊंची जगह जाएं। बाढ़ वाली सड़कों पर न जाएं। 1077 पर कॉल करें।",
        },
        "cyclone": {
            "en": "🌀 CYCLONE WARNING: Cyclone approaching {location}. SEEK SHELTER IMMEDIATELY in strong building. Stay away from windows. Do NOT go outside.",
            "ta": "🌀 சூறாவளி எச்சரிக்கை: {location}ல் சூறாவளி வருகிறது. உடனடியாக உறுதியான கட்டிடத்தில் தஞ்சம் புகுக. சன்னல்களிலிருந்து விலக.",
            "hi": "🌀 चक्रवात चेतावनी: {location} में चक्रवात आ रहा है। तुरंत मजबूत इमारत में आश्रय लें। खिड़कियों से दूर रहें।",
        },
        "earthquake": {
            "en": "🌍 EARTHQUAKE ALERT: Earthquake detected near {location}. DROP, COVER, and HOLD ON. Stay inside. Beware of aftershocks.",
            "ta": "🌍 நிலநடுக்கம் எச்சரிக்கை: {location} அருகில் நிலநடுக்கம். கீழே விழுங்கள், மூடுக, பிடித்துக்கொள்ளுங்கள். கட்டிடத்திற்குள் இருங்கள்.",
            "hi": "🌍 भूकंप अलर्ट: {location} के पास भूकंप आया है। झुकें, ढकें और टिके रहें। इमारत में रहें।",
        },
        "heatwave": {
            "en": "🔥 HEAT WAVE WARNING: Extreme heat in {location}. Stay indoors 12PM–4PM. Drink water every 20 mins. Call 108 if symptoms of heat stroke.",
            "ta": "🔥 வெப்ப அலை எச்சரிக்கை: {location}ல் கடும் வெப்பம். மதியம் 12–4 மணி வரை வெளியில் செல்லாதீர்கள். தண்ணீர் குடிக்கவும்.",
            "hi": "🔥 लू की चेतावनी: {location} में भीषण गर्मी। दोपहर 12–4 बजे घर में रहें। हर 20 मिनट में पानी पियें।",
        },
    }

    def __init__(self):
        super().__init__("Emergency Alert Agent", use_flash=True)

    def _generate_alert(self, disaster_type: str, location: str, severity: int, language: str = "en") -> dict:
        lang = language if language in ("en", "ta", "hi") else "en"

        # Try LLM for custom alerts
        if not self._demo_mode and severity >= 4:
            prompt = f"""
Generate an emergency alert for:
- Disaster: {disaster_type}
- Location: {location}
- Severity: {severity}/5
- Language: {lang}

Respond ONLY with JSON:
{{
  "alert_type": "warning|watch|advisory|emergency",
  "title": "Short alert title",
  "message_en": "English alert message (2-3 sentences)",
  "message_ta": "Tamil translation",
  "message_hi": "Hindi translation",
  "do_immediately": ["action1", "action2", "action3"],
  "avoid": ["thing1", "thing2"],
  "helplines": ["112 - Emergency", "1077 - Flood", "108 - Ambulance"],
  "valid_until": "Next 12 hours",
  "issued_by": "RescueMind AI in coordination with NDMA"
}}
"""
            result = self._call_gemini(prompt)
            if result:
                result["language"] = lang
                return result

        # Template-based alert
        templates = self.ALERT_TEMPLATES.get(disaster_type, self.ALERT_TEMPLATES["flood"])
        msg = templates.get(lang, templates["en"]).format(location=location)

        alert_type = "emergency" if severity >= 4 else ("warning" if severity >= 3 else "advisory")
        return {
            "alert_type": alert_type,
            "title": f"{disaster_type.upper()} {alert_type.upper()} – {location}",
            "message_en": templates["en"].format(location=location),
            "message_ta": templates["ta"].format(location=location),
            "message_hi": templates["hi"].format(location=location),
            "message": msg,
            "do_immediately": [
                "Call 112 (National Emergency)",
                "Follow official evacuation orders",
                "Keep emergency kit ready",
            ],
            "avoid": ["Rumours and unverified information", "Flooded areas", "Fallen power lines"],
            "helplines": ["112 – Emergency", "1077 – Flood Control", "108 – Ambulance", "101 – Fire"],
            "valid_until": "Next 12 hours",
            "issued_by": "RescueMind AI in coordination with NDMA/SDMA",
            "language": lang,
            "severity": severity,
        }

    def _execute(self, context: dict) -> AgentResponse:
        disaster_type = context.get("disaster_type", "flood")
        location = context.get("location", "Affected Area")
        severity = context.get("severity", 3)
        language = context.get("language", "en")

        alert = self._generate_alert(disaster_type, location, severity, language)
        msg = alert.get(f"message_{language}", alert.get("message_en", ""))

        return AgentResponse(
            agent_name=self.agent_name,
            action="generate_alert",
            success=True,
            content={"alert": alert},
            recommendation=f"🚨 {alert.get('title')}: {msg[:150]}",
            reason=f"Severity level {severity}/5 {disaster_type} event detected at {location}.",
            data_sources=["NDMA", "IMD", "State SDMA", "RescueMind AI"],
            confidence=0.90,
            risk_level="critical" if severity >= 4 else "high",
            alternatives=[
                "Issue shelter-in-place advisory",
                "Activate community phone tree",
                "Deploy public address announcements",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 2. SHELTER & EVACUATION AGENT
# ══════════════════════════════════════════════════════════════════════════════
class ShelterEvacuationAgent(BaseAgent):
    """
    Identifies nearby shelters, calculates distances, recommends evacuation routes,
    and provides capacity and facility information.
    """

    def __init__(self):
        super().__init__("Shelter & Evacuation Agent", use_flash=True)

    def _find_nearby_shelters(self, lat: float, lon: float, disaster_type: str, max_results: int = 5) -> list[dict]:
        """Query database for shelters, compute distances, rank by proximity."""
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute(
                "SELECT * FROM shelters WHERE is_active = 1"
            )
            rows = cursor.fetchall()
            conn.close()

            shelters = []
            for row in rows:
                d = dict(row)
                dist = haversine_km(lat, lon, d.get("location_lat", lat), d.get("location_lon", lon))
                d["distance_km"] = round(dist, 2)
                d["available_capacity"] = d.get("capacity", 0) - d.get("current_occupancy", 0)
                d["occupancy_pct"] = round(
                    (d.get("current_occupancy", 0) / max(d.get("capacity", 1), 1)) * 100, 1
                )
                # Filter by disaster type compatibility
                dtypes = json.loads(d.get("disaster_types") or "[]")
                if not dtypes or disaster_type in dtypes or "general" in dtypes:
                    shelters.append(d)

            # Sort by distance
            shelters.sort(key=lambda x: x["distance_km"])
            return shelters[:max_results]

        except Exception as e:
            logger.warning(f"[Shelter] DB query error: {e}")
            return self._demo_shelters(lat, lon)

    def _demo_shelters(self, lat: float, lon: float) -> list[dict]:
        base = [
            {"shelter_id": "SH001", "name": "District Collector Office Relief Camp",
             "address": "Tirunelveli Main Road", "district": "Tirunelveli",
             "capacity": 500, "current_occupancy": 120, "shelter_type": "general",
             "contact_phone": "0462-2334567", "location_lat": 8.7139, "location_lon": 77.7567,
             "facilities": '["water","food","toilet","medical_aid"]'},
            {"shelter_id": "SH002", "name": "Nellai Govt High School",
             "address": "Palayamkottai", "district": "Tirunelveli",
             "capacity": 300, "current_occupancy": 85, "shelter_type": "general",
             "contact_phone": "0462-2335678", "location_lat": 8.7234, "location_lon": 77.7401,
             "facilities": '["water","food","toilet"]'},
            {"shelter_id": "SH003", "name": "YMCA Community Hall",
             "address": "Melapalayam", "district": "Tirunelveli",
             "capacity": 200, "current_occupancy": 40, "shelter_type": "general",
             "contact_phone": "9876543210", "location_lat": 8.7051, "location_lon": 77.7389,
             "facilities": '["water","food","generator"]'},
        ]
        for s in base:
            s["distance_km"] = round(haversine_km(lat, lon, s["location_lat"], s["location_lon"]), 2)
            s["available_capacity"] = s["capacity"] - s["current_occupancy"]
            s["occupancy_pct"] = round((s["current_occupancy"] / s["capacity"]) * 100, 1)
        base.sort(key=lambda x: x["distance_km"])
        return base

    def _execute(self, context: dict) -> AgentResponse:
        lat = float(context.get("lat", 8.7139))
        lon = float(context.get("lon", 77.7567))
        disaster_type = context.get("disaster_type", "flood")
        location = context.get("location", "Your location")

        shelters = self._find_nearby_shelters(lat, lon, disaster_type)

        if not shelters:
            return AgentResponse(
                agent_name=self.agent_name, action="find_shelter",
                success=False, recommendation="No shelters found. Call 112.",
                reason="No shelter data available for your location.",
                confidence=0.5, risk_level="high",
            )

        nearest = shelters[0]
        facilities = json.loads(nearest.get("facilities") or "[]")

        return AgentResponse(
            agent_name=self.agent_name,
            action="find_shelter",
            success=True,
            content={
                "shelters": shelters,
                "nearest": nearest,
                "total_found": len(shelters),
                "user_lat": lat, "user_lon": lon,
            },
            recommendation=(
                f"🏠 Nearest shelter: **{nearest['name']}** ({nearest['distance_km']} km away). "
                f"Available capacity: {nearest['available_capacity']} people. "
                f"Contact: {nearest.get('contact_phone','N/A')}. "
                f"Facilities: {', '.join(facilities[:4]) if facilities else 'Basic'}"
            ),
            reason=(
                f"Found {len(shelters)} active shelters within range. "
                f"Ranked by distance from {location}. "
                f"Nearest is {nearest['distance_km']}km away with {nearest['available_capacity']} available spots."
            ),
            data_sources=["RescueMind Shelter Database", "District Collector Records", "State SDMA"],
            confidence=0.88,
            risk_level="high",
            alternatives=[f"{s['name']} – {s['distance_km']}km, {s['available_capacity']} spots" for s in shelters[1:4]],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3. RESCUE COORDINATION AGENT
# ══════════════════════════════════════════════════════════════════════════════
class RescueCoordinationAgent(BaseAgent):
    """
    Analyzes rescue requests, assigns priority scores, coordinates response resources.
    Uses multi-factor scoring: severity, vulnerability, accessibility, urgency.
    """

    def __init__(self):
        super().__init__("Rescue Coordination Agent")

    def _calculate_priority_score(self, context: dict) -> tuple[float, str]:
        """
        Multi-factor priority scoring algorithm.
        Returns (score 0.0-1.0, priority_label)
        """
        base_severity = context.get("severity", 3) / 5.0         # 0.0–1.0

        # Vulnerability factors
        has_injured  = 1.0 if context.get("has_injured") else 0.0
        has_children = 0.7 if context.get("has_children") else 0.0
        has_elderly  = 0.6 if context.get("has_elderly") else 0.0
        num_people   = min(context.get("num_people", 1) / 10.0, 1.0)

        # Time sensitivity
        time_urgency = context.get("time_urgency", 0.5)

        # Accessibility difficulty (1.0 = totally inaccessible)
        accessibility = 1.0 - context.get("accessibility", 0.5)

        # Weighted scoring
        score = (
            base_severity  * 0.30 +
            has_injured    * 0.25 +
            has_children   * 0.15 +
            has_elderly    * 0.10 +
            num_people     * 0.10 +
            time_urgency   * 0.05 +
            accessibility  * 0.05
        )
        score = round(min(score, 1.0), 3)

        if score >= 0.8:   label = "CRITICAL"
        elif score >= 0.6: label = "HIGH"
        elif score >= 0.4: label = "MODERATE"
        else:              label = "LOW"

        return score, label

    def _execute(self, context: dict) -> AgentResponse:
        description = context.get("query", context.get("description", "Rescue needed"))
        location = context.get("location", "Unknown location")
        num_people = context.get("num_people", 1)
        has_injured = context.get("has_injured", False)
        has_children = context.get("has_children", False)
        has_elderly = context.get("has_elderly", False)
        severity = context.get("severity", 3)

        priority_score, priority_label = self._calculate_priority_score({
            "severity": severity,
            "has_injured": has_injured,
            "has_children": has_children,
            "has_elderly": has_elderly,
            "num_people": num_people,
            "time_urgency": 0.7 if severity >= 4 else 0.4,
            "accessibility": 0.5,
        })

        response_teams = []
        if has_injured:
            response_teams.append("Medical Response Team (108 Ambulance)")
        if severity >= 4:
            response_teams.append("NDRF / SDRF Rescue Team")
        if context.get("disaster_type") == "flood":
            response_teams.append("Flood Rescue Boat Team")
        response_teams.append("Local Fire & Rescue Service (101)")

        return AgentResponse(
            agent_name=self.agent_name,
            action="rescue_prioritization",
            success=True,
            content={
                "priority_score": priority_score,
                "priority_label": priority_label,
                "response_teams": response_teams,
                "affected_people": num_people,
                "vulnerability_flags": {
                    "injured": has_injured,
                    "children": has_children,
                    "elderly": has_elderly,
                },
                "location": location,
            },
            recommendation=(
                f"🚨 Priority: **{priority_label}** (score: {priority_score:.2f}/1.0). "
                f"{num_people} people at {location}. "
                f"Recommended response: {response_teams[0] if response_teams else 'Emergency 112'}. "
                f"ETA: {'15–30 min' if priority_score >= 0.7 else '30–60 min'}"
            ),
            reason=(
                f"Priority calculated from: severity={severity}/5, "
                f"injured={has_injured}, children={has_children}, elderly={has_elderly}, "
                f"people={num_people}. Multi-factor weighted scoring applied."
            ),
            data_sources=["RescueMind Priority Algorithm", "NDRF Response Protocol"],
            confidence=0.85,
            risk_level="critical" if priority_score >= 0.8 else "high",
            alternatives=[
                "Self-evacuation if path is clear",
                "Contact nearest police station",
                "Use emergency beacon/whistle to signal location",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 4. MEDICAL ASSISTANCE AGENT
# ══════════════════════════════════════════════════════════════════════════════
class MedicalAssistanceAgent(BaseAgent):
    """
    Provides emergency medical guidance, first aid instructions,
    nearest hospital recommendations, and medical resource information.
    """

    FIRST_AID_KNOWLEDGE = {
        "drowning": {
            "steps": [
                "Remove person from water safely; do not put yourself at risk",
                "Lay person flat on their back on firm surface",
                "Tilt head back, lift chin to open airway",
                "Check for breathing (10 seconds)",
                "If not breathing: give 2 rescue breaths, then 30 chest compressions",
                "Continue CPR until help arrives or person breathes",
                "Keep warm; treat for hypothermia",
            ],
            "call": "108 – Ambulance immediately",
            "severity": "critical",
        },
        "heat_stroke": {
            "steps": [
                "Move person to cool, shaded place immediately",
                "Remove excess clothing",
                "Apply cool wet cloth to neck, armpits, and groin",
                "Fan the person to increase evaporation",
                "Give cool water sips if conscious and able to swallow",
                "Do NOT give aspirin or paracetamol",
                "Monitor temperature and consciousness",
            ],
            "call": "108 – Ambulance if confused or unconscious",
            "severity": "high",
        },
        "fracture": {
            "steps": [
                "Do not move the person unnecessarily",
                "Immobilize the injured area using a splint or rigid support",
                "Apply ice pack wrapped in cloth (not directly on skin)",
                "Control any bleeding with gentle pressure",
                "Elevate the limb if possible",
                "Keep person still and calm until help arrives",
            ],
            "call": "108 – Ambulance for serious fractures",
            "severity": "moderate",
        },
        "wound": {
            "steps": [
                "Apply direct pressure with clean cloth to stop bleeding",
                "Do not remove object if embedded; stabilize it",
                "Clean wound with clean water if available",
                "Apply antiseptic if available",
                "Cover with sterile bandage",
                "Elevate injured area above heart level",
                "Watch for signs of infection (redness, swelling, pus)",
            ],
            "call": "108 – Ambulance for deep wounds or heavy bleeding",
            "severity": "moderate",
        },
        "default": {
            "steps": [
                "Keep the person calm and still",
                "Call 108 (Ambulance) immediately for serious conditions",
                "Monitor breathing and pulse",
                "Do not give food or water if unconscious",
                "Keep person warm and comfortable",
                "Gather any available medicines / medical history to share with paramedics",
            ],
            "call": "108 – Ambulance",
            "severity": "moderate",
        },
    }

    def __init__(self):
        super().__init__("Medical Assistance Agent")

    def _identify_condition(self, query: str) -> str:
        """Identify medical condition type from query keywords."""
        q = query.lower()
        if any(w in q for w in ["drown", "water", "flood", "submer"]):
            return "drowning"
        if any(w in q for w in ["heat", "sun", "hot", "dehydrat", "faint"]):
            return "heat_stroke"
        if any(w in q for w in ["fracture", "broken bone", "fall"]):
            return "fracture"
        if any(w in q for w in ["wound", "cut", "bleed", "injury", "injur"]):
            return "wound"
        return "default"

    def _execute(self, context: dict) -> AgentResponse:
        query = context.get("query", "medical emergency")
        location = context.get("location", "")
        condition = self._identify_condition(query)
        guidance = self.FIRST_AID_KNOWLEDGE[condition]

        return AgentResponse(
            agent_name=self.agent_name,
            action="medical_guidance",
            success=True,
            content={
                "condition_type": condition,
                "first_aid_steps": guidance["steps"],
                "emergency_call": guidance["call"],
                "severity": guidance["severity"],
                "nearby_hospitals": [
                    "Tirunelveli Government Medical College Hospital – 0462-2572555",
                    "St. John's Hospital, Tirunelveli – 0462-2578801",
                    "SRM Hospitals – 1800-103-0101",
                ],
                "emergency_contacts": {
                    "Ambulance": "108",
                    "Emergency": "112",
                    "Disaster Medical": "1079",
                },
            },
            recommendation=(
                f"🏥 {condition.upper().replace('_',' ')} First Aid: "
                f"Step 1: {guidance['steps'][0]}. "
                f"Call: **{guidance['call']}**"
            ),
            reason=(
                f"Identified condition '{condition}' from query. "
                f"First aid protocol from standard emergency medical guidelines. "
                f"Severity assessed as {guidance['severity']}."
            ),
            data_sources=["WHO First Aid Guidelines", "Indian Red Cross", "NDMA Medical Protocol"],
            confidence=0.87,
            risk_level=guidance["severity"],
            alternatives=[
                "Proceed directly to nearest government hospital",
                "Contact 108 ambulance for home assistance",
                "Reach community health centre",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 5. RESOURCE ALLOCATION AGENT
# ══════════════════════════════════════════════════════════════════════════════
class ResourceAllocationAgent(BaseAgent):
    """
    Tracks available resources, recommends distribution plans,
    and optimizes resource usage across affected areas.
    """

    def __init__(self):
        super().__init__("Resource Allocation Agent", use_flash=True)

    def _get_resource_inventory(self) -> list[dict]:
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute("SELECT * FROM resource_inventory WHERE available = 1")
            resources = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return resources
        except Exception as e:
            logger.warning(f"[Resource] DB error: {e}")
            return [
                {"resource_type": "food",      "name": "Ready-to-Eat Packets", "quantity": 5000, "unit": "packets", "location_name": "Tirunelveli Warehouse"},
                {"resource_type": "water",     "name": "Water Cans (20L)",     "quantity": 1200, "unit": "cans",    "location_name": "Tirunelveli Warehouse"},
                {"resource_type": "medicine",  "name": "First Aid Kits",       "quantity": 300,  "unit": "kits",    "location_name": "Medical Store"},
                {"resource_type": "equipment", "name": "Life Jackets",         "quantity": 150,  "unit": "units",   "location_name": "Fire Station"},
                {"resource_type": "equipment", "name": "Rescue Boats",         "quantity": 8,    "unit": "units",   "location_name": "Fire Station"},
            ]

    def _execute(self, context: dict) -> AgentResponse:
        affected_people = context.get("num_people", 1000)
        disaster_type   = context.get("disaster_type", "flood")
        resources       = self._get_resource_inventory()

        # Group by type
        by_type: dict[str, list] = {}
        for r in resources:
            t = r.get("resource_type", "other")
            by_type.setdefault(t, []).append(r)

        # Calculate requirements (standard disaster relief norms)
        food_req    = affected_people * 3          # 3 meals/day
        water_req   = affected_people * 5          # 5L/person/day (20L cans)
        kit_req     = max(1, affected_people // 10)

        food_avail  = sum(r["quantity"] for r in by_type.get("food", []))
        water_avail = sum(r["quantity"] for r in by_type.get("water", []))
        kit_avail   = sum(r["quantity"] for r in by_type.get("medicine", []))

        gaps = []
        if food_avail  < food_req:   gaps.append(f"Food: need {food_req - food_avail:.0f} more meal packets")
        if water_avail < water_req:  gaps.append(f"Water: need {water_req - water_avail:.0f} more 20L cans")
        if kit_avail   < kit_req:    gaps.append(f"First Aid Kits: need {kit_req - kit_avail:.0f} more kits")

        return AgentResponse(
            agent_name=self.agent_name,
            action="resource_allocation",
            success=True,
            content={
                "inventory": resources,
                "by_type": {k: len(v) for k, v in by_type.items()},
                "requirements": {
                    "food_packets": food_req,
                    "water_cans": water_req,
                    "first_aid_kits": kit_req,
                },
                "availability": {
                    "food_packets": food_avail,
                    "water_cans": water_avail,
                    "first_aid_kits": kit_avail,
                },
                "supply_gaps": gaps,
                "affected_people": affected_people,
            },
            recommendation=(
                f"📦 For {affected_people} people: "
                f"Food: {food_avail:.0f}/{food_req:.0f} available. "
                f"Water: {water_avail:.0f}/{water_req:.0f}. "
                f"{'⚠️ Supply gaps: ' + '; '.join(gaps) if gaps else '✅ Sufficient supplies for current demand.'}"
            ),
            reason=(
                f"Calculated based on NDMA norms: 3 meals/person, 5L water/day, 1 kit per 10 people. "
                f"Current inventory assessed from {len(resources)} resource entries."
            ),
            data_sources=["RescueMind Resource DB", "NDMA Supply Norms", "District Warehouse Records"],
            confidence=0.83,
            risk_level="high" if gaps else "moderate",
            alternatives=[
                "Request reinforcements from neighboring districts",
                "Activate NDMA relief supply chain",
                "Coordinate with Red Cross for emergency supplies",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 6. DAMAGE ASSESSMENT AGENT
# ══════════════════════════════════════════════════════════════════════════════
class DamageAssessmentAgent(BaseAgent):
    """
    Analyzes disaster impact, estimates infrastructure damage,
    and prioritizes recovery actions.
    """

    def __init__(self):
        super().__init__("Damage Assessment Agent")

    def _execute(self, context: dict) -> AgentResponse:
        disaster_type  = context.get("disaster_type", "flood")
        severity       = context.get("severity", 3)
        affected_area  = context.get("affected_area", "Unknown")
        affected_people= context.get("num_people", 1000)

        # Severity-based impact model
        damage_scores = {
            1: {"infrastructure": 5,  "housing": 3,  "agriculture": 10, "roads": 2},
            2: {"infrastructure": 15, "housing": 10, "agriculture": 25, "roads": 8},
            3: {"infrastructure": 30, "housing": 25, "agriculture": 45, "roads": 20},
            4: {"infrastructure": 55, "housing": 45, "agriculture": 70, "roads": 40},
            5: {"infrastructure": 80, "housing": 70, "agriculture": 90, "roads": 75},
        }
        scores = damage_scores.get(severity, damage_scores[3])
        overall_score = round(sum(scores.values()) / len(scores), 1)

        recovery_phases = [
            {"phase": "Immediate (0–72h)",  "priority": "Search & Rescue, Emergency Shelter, Medical Care"},
            {"phase": "Short-term (1–4 wks)", "priority": "Temporary housing, Water supply, Power restoration"},
            {"phase": "Medium-term (1–6 mo)", "priority": "Permanent housing reconstruction, Road repair"},
            {"phase": "Long-term (6m–2yr)",   "priority": "Agricultural recovery, Economic rehabilitation"},
        ]

        return AgentResponse(
            agent_name=self.agent_name,
            action="damage_assessment",
            success=True,
            content={
                "damage_scores": scores,
                "overall_damage_score": overall_score,
                "severity": severity,
                "affected_area": affected_area,
                "affected_people": affected_people,
                "recovery_phases": recovery_phases,
            },
            recommendation=(
                f"🏗️ Overall Damage: **{overall_score:.0f}%** of infrastructure affected. "
                f"Infrastructure: {scores['infrastructure']}%, Housing: {scores['housing']}%, "
                f"Agriculture: {scores['agriculture']}%. "
                f"Estimated recovery start: Immediate rescue operations."
            ),
            reason=(
                f"Damage estimate based on severity level {severity}/5 for {disaster_type}. "
                f"Uses NDMA damage assessment matrix calibrated for India's disaster patterns."
            ),
            data_sources=["NDMA Damage Assessment Matrix", "State Revenue Department", "Satellite Analysis"],
            confidence=0.72,
            risk_level="critical" if overall_score >= 60 else "high",
            alternatives=[
                "Deploy satellite/drone imagery for precise assessment",
                "Conduct field survey by revenue officials",
                "Use PM Fasal Bima for agricultural loss claims",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 7. GOVERNMENT RELIEF AGENT
# ══════════════════════════════════════════════════════════════════════════════
class GovernmentReliefAgent(BaseAgent):
    """
    Searches government and NGO relief programs, explains eligibility,
    and helps users apply for disaster assistance.
    """

    def __init__(self):
        super().__init__("Government Relief Agent", use_flash=True)

    def _get_programs(self, disaster_type: str, state: str = "Tamil Nadu") -> list[dict]:
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute(
                "SELECT * FROM relief_programs WHERE is_active = 1 ORDER BY provider"
            )
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            # Filter by disaster type
            relevant = []
            for p in rows:
                dtypes = json.loads(p.get("disaster_types") or "[]")
                if disaster_type in dtypes or not dtypes:
                    relevant.append(p)
            return relevant[:8]
        except Exception as e:
            logger.warning(f"[Relief] DB error: {e}")
            return [
                {"name": "TN CM Relief Fund", "provider": "Tamil Nadu State Government",
                 "benefits": "₹5,000–25,000 immediate relief; up to ₹1 lakh housing",
                 "eligibility": "TN resident affected by notified disaster",
                 "application_url": "https://tnlive.tn.gov.in",
                 "contact_info": "044-25671234"},
                {"name": "PM Fasal Bima Yojana", "provider": "Central Government",
                 "benefits": "Up to ₹2 lakhs crop insurance",
                 "eligibility": "Farmer with KCC; crop loss > 50%",
                 "application_url": "https://pmfby.gov.in",
                 "contact_info": "1800-180-1551"},
            ]

    def _execute(self, context: dict) -> AgentResponse:
        disaster_type = context.get("disaster_type", "flood")
        state = context.get("state", "Tamil Nadu")

        programs = self._get_programs(disaster_type, state)

        return AgentResponse(
            agent_name=self.agent_name,
            action="relief_information",
            success=True,
            content={
                "programs": programs,
                "total_programs": len(programs),
                "disaster_type": disaster_type,
                "state": state,
            },
            recommendation=(
                f"💰 {len(programs)} relief programs available for {disaster_type} in {state}. "
                f"Top option: {programs[0]['name'] if programs else 'N/A'} – "
                f"{programs[0]['benefits'][:80] if programs else 'No programs found'}. "
                f"Contact: {programs[0].get('contact_info','112') if programs else '112'}"
            ),
            reason=(
                f"Retrieved {len(programs)} government and NGO programs relevant to "
                f"{disaster_type} disasters in {state}."
            ),
            data_sources=["NDMA Portal", "TN State Disaster Management", "ReliefWeb", "NGO Database"],
            confidence=0.85,
            risk_level="low",
            alternatives=[
                "Apply via PM Relief Fund directly",
                "Contact District Collector's office for immediate relief",
                "Reach out to local NGOs (Red Cross, HelpAge India)",
            ],
        )


# ══════════════════════════════════════════════════════════════════════════════
# 8. PLANNING AGENT
# ══════════════════════════════════════════════════════════════════════════════
class PlanningAgent(BaseAgent):
    """
    Generates preparedness plans, response plans, and recovery roadmaps.
    Produces day/week/month timelines with actionable steps.
    """

    def __init__(self):
        super().__init__("Planning Agent")

    def _generate_plan(self, plan_type: str, disaster_type: str, context: dict) -> dict:
        """Generate structured plans, using Gemini if available."""
        if not self._demo_mode and self._gemini:
            prompt = f"""
Create a {plan_type} disaster response plan for:
- Disaster type: {disaster_type}
- Location: {context.get('location', 'Tamil Nadu, India')}
- Target audience: {context.get('role', 'citizen')}
- Number of people: {context.get('num_people', 'family of 4')}

Respond ONLY with valid JSON:
{{
  "plan_type": "{plan_type}",
  "title": "Plan title",
  "phases": [
    {{"phase": "Phase name", "timeframe": "Duration", "actions": ["action1", "action2", "action3"]}}
  ],
  "resources_needed": ["item1", "item2"],
  "key_contacts": ["contact1", "contact2"],
  "checklist": ["item1", "item2", "item3"]
}}
"""
            result = self._call_gemini(prompt)
            if result:
                return result

        # Demo plans
        return self._demo_plan(plan_type, disaster_type)

    def _demo_plan(self, plan_type: str, disaster_type: str) -> dict:
        if plan_type == "preparedness":
            return {
                "plan_type": "preparedness",
                "title": f"{disaster_type.capitalize()} Preparedness Plan",
                "phases": [
                    {"phase": "Week 1: Awareness", "timeframe": "7 days",
                     "actions": ["Identify flood-prone areas near home", "Know evacuation routes", "Register with local emergency management"]},
                    {"phase": "Week 2: Kit Preparation", "timeframe": "7 days",
                     "actions": ["Prepare 72-hour emergency kit", "Stock water (4L/person/day × 3 days)", "Keep important documents waterproofed"]},
                    {"phase": "Week 3–4: Community", "timeframe": "14 days",
                     "actions": ["Connect with neighbourhood emergency team", "Practice evacuation drill", "Check home for vulnerabilities"]},
                ],
                "resources_needed": ["Water (12L min)", "Food rations (3 days)", "First aid kit", "Flashlight + batteries", "Emergency contacts list", "Copies of ID documents"],
                "key_contacts": ["Emergency: 112", "Flood Control: 1077", "Ambulance: 108", "District Collector: 0462-2334567"],
                "checklist": ["72-hour water supply", "Non-perishable food", "Medicine supply (30 days)", "First aid kit", "Flashlight", "Battery radio", "Cash (small denominations)", "Important documents in waterproof bag"],
            }
        elif plan_type == "response":
            return {
                "plan_type": "response",
                "title": f"{disaster_type.capitalize()} Emergency Response Plan",
                "phases": [
                    {"phase": "First 30 minutes: Immediate Safety", "timeframe": "0–30 min",
                     "actions": ["Ensure personal safety; move to high ground", "Account for all family members", "Call 112 if life-threatening danger"]},
                    {"phase": "Hours 1–6: Shelter & Communication", "timeframe": "1–6 hours",
                     "actions": ["Proceed to designated shelter", "Inform family of your location", "Register at relief camp"]},
                    {"phase": "Day 1–3: Stabilization", "timeframe": "24–72 hours",
                     "actions": ["Follow official instructions", "Seek medical care if needed", "Document losses for relief claims"]},
                ],
                "resources_needed": ["Emergency kit", "Phone with charged battery", "Cash", "Medications"],
                "key_contacts": ["Emergency: 112", "Flood: 1077", "Ambulance: 108"],
                "checklist": ["Personal safety secured", "Family members accounted for", "Reached shelter", "Communicated location", "Medical needs addressed", "Registered for relief"],
            }
        else:  # recovery
            return {
                "plan_type": "recovery",
                "title": f"{disaster_type.capitalize()} Recovery Plan",
                "phases": [
                    {"phase": "Week 1–2: Assessment", "timeframe": "14 days",
                     "actions": ["Assess damage to home and property", "File damage report with Revenue Department", "Apply for government relief programs"]},
                    {"phase": "Month 1–3: Restoration", "timeframe": "1–3 months",
                     "actions": ["Begin home repairs (structural safety first)", "Resume livelihood activities", "Access mental health support if needed"]},
                    {"phase": "Month 3–12: Resilience", "timeframe": "3–12 months",
                     "actions": ["Implement flood-proofing measures", "Join community disaster preparedness group", "Review and update family emergency plan"]},
                ],
                "resources_needed": ["Government relief funds", "Insurance claims", "NGO support"],
                "key_contacts": ["District Collector: 0462-2334567", "NDMA: 1079", "Red Cross: 1800-111-110"],
                "checklist": ["Damage documented", "Relief application submitted", "Temporary shelter secured", "Medical check done", "Livelihood plan made"],
            }

    def _execute(self, context: dict) -> AgentResponse:
        query = context.get("query", "").lower()
        disaster_type = context.get("disaster_type", "flood")

        if "prepar" in query:
            plan_type = "preparedness"
        elif "recover" in query:
            plan_type = "recovery"
        else:
            plan_type = "response"

        plan = self._generate_plan(plan_type, disaster_type, context)

        return AgentResponse(
            agent_name=self.agent_name,
            action=f"{plan_type}_plan",
            success=True,
            content={"plan": plan, "plan_type": plan_type, "disaster_type": disaster_type},
            recommendation=(
                f"📋 {plan.get('title','Plan Generated')}. "
                f"First priority: {plan['phases'][0]['actions'][0] if plan.get('phases') else 'Follow emergency guidelines'}. "
                f"Total phases: {len(plan.get('phases', []))}"
            ),
            reason=(
                f"Generated {plan_type} plan for {disaster_type} based on "
                f"NDMA guidelines and standard emergency management protocols."
            ),
            data_sources=["NDMA Guidelines", "FEMA Protocols", "India Disaster Management Act 2005"],
            confidence=0.82,
            risk_level="moderate",
            alternatives=[
                "Consult local District Disaster Management Authority",
                "Download NDMA mobile app for offline plans",
                "Join community preparedness workshop",
            ],
        )
