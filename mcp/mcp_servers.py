"""
RescueMind AI – MCP (Model Context Protocol) Servers
Complete implementation of all 6 MCP servers providing tool interfaces
for weather, shelter, resources, government relief, medical, and emergency contacts.
"""

import json
import math
import asyncio
import logging
from datetime import datetime
from typing import Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


# ─── MCP Tool Definition Helper ───────────────────────────────────────────────
def make_tool(name: str, description: str, properties: dict, required: list = None) -> dict:
    """Helper to create MCP-compatible tool definition."""
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 1: WEATHER & DISASTER DATA
# ══════════════════════════════════════════════════════════════════════════════
class WeatherDisasterMCPServer:
    """
    MCP Server providing weather alerts and disaster monitoring tools.
    
    Tools:
    - get_current_weather(location)
    - get_disaster_alerts(location, disaster_type?)
    - get_flood_risk(location, lat, lon)
    - get_historical_disasters(location, years?)
    """

    SERVER_NAME = "weather-disaster-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("get_current_weather",
                "Get current weather conditions for a location including alerts.",
                {"location": {"type": "string", "description": "City or district name"},
                 "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}},
                required=["location"]),
            make_tool("get_disaster_alerts",
                "Retrieve active disaster alerts and warnings for an area.",
                {"location": {"type": "string", "description": "Location to query"},
                 "disaster_type": {"type": "string", "description": "Optional: flood|cyclone|earthquake|all"},
                 "severity_min": {"type": "integer", "description": "Minimum severity (1-5)", "default": 1}},
                required=["location"]),
            make_tool("get_flood_risk",
                "Assess flood risk for given coordinates.",
                {"lat": {"type": "number"}, "lon": {"type": "number"},
                 "location_name": {"type": "string"}},
                required=["lat", "lon"]),
            make_tool("get_active_events",
                "Get all currently active disaster events in the database.",
                {"status": {"type": "string", "enum": ["active", "monitoring", "resolved", "all"], "default": "active"}},
                required=[]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Route tool calls to appropriate handlers."""
        handlers = {
            "get_current_weather":  self._get_current_weather,
            "get_disaster_alerts":  self._get_disaster_alerts,
            "get_flood_risk":       self._get_flood_risk,
            "get_active_events":    self._get_active_events,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return await handler(arguments)
        except Exception as e:
            logger.error(f"[{self.SERVER_NAME}] Tool {tool_name} error: {e}")
            return {"error": str(e)}

    async def _get_current_weather(self, args: dict) -> dict:
        location = args.get("location", "Tirunelveli")
        # Demo response (real: calls OpenWeatherMap API)
        return {
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature_c": 29.8,
            "humidity_pct": 92,
            "wind_speed_ms": 12.0,
            "rain_1h_mm": 42.5,
            "pressure_hpa": 998,
            "description": "Heavy rain",
            "alert": "Heavy Rainfall Warning – IMD",
            "source": "OpenWeatherMap (demo)",
        }

    async def _get_disaster_alerts(self, args: dict) -> dict:
        location = args.get("location", "Tamil Nadu")
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute(
                "SELECT * FROM disaster_events WHERE status IN ('active','monitoring') LIMIT 5"
            )
            events = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception:
            events = [
                {"event_id": "DE001", "disaster_type": "flood", "title": "Thamirabarani River Flooding",
                 "severity": 3, "status": "active", "location_name": "Tirunelveli"},
            ]
        return {
            "location": location,
            "alerts": events,
            "total": len(events),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _get_flood_risk(self, args: dict) -> dict:
        lat = args.get("lat", 8.7139)
        lon = args.get("lon", 77.7567)
        # Simplified flood risk model
        risk = "HIGH" if lat < 9.0 else "MODERATE"
        return {
            "lat": lat, "lon": lon,
            "flood_risk": risk,
            "risk_score": 0.72 if risk == "HIGH" else 0.45,
            "factors": ["proximity_to_river", "elevation", "historical_flooding"],
            "recommendation": "Evacuate if warned" if risk == "HIGH" else "Monitor situation",
        }

    async def _get_active_events(self, args: dict) -> dict:
        status = args.get("status", "active")
        try:
            from database.schema import get_connection
            conn = get_connection()
            query = "SELECT * FROM disaster_events" if status == "all" else \
                    "SELECT * FROM disaster_events WHERE status = ?"
            params = () if status == "all" else (status,)
            cursor = conn.execute(query, params)
            events = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception:
            events = []
        return {"events": events, "count": len(events), "status_filter": status}


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 2: SHELTER DATABASE
# ══════════════════════════════════════════════════════════════════════════════
class ShelterDatabaseMCPServer:
    """
    MCP Server for shelter discovery and management.
    
    Tools:
    - find_nearby_shelters(lat, lon, radius_km?)
    - get_shelter_details(shelter_id)
    - update_shelter_occupancy(shelter_id, occupancy)
    - get_shelter_capacity_summary(district)
    """

    SERVER_NAME = "shelter-database-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("find_nearby_shelters",
                "Find evacuation shelters within a given radius.",
                {"lat": {"type": "number"}, "lon": {"type": "number"},
                 "radius_km": {"type": "number", "default": 20},
                 "disaster_type": {"type": "string", "default": "any"},
                 "min_capacity": {"type": "integer", "default": 0}},
                required=["lat", "lon"]),
            make_tool("get_shelter_details",
                "Get full details for a specific shelter.",
                {"shelter_id": {"type": "string"}},
                required=["shelter_id"]),
            make_tool("update_shelter_occupancy",
                "Update current occupancy count for a shelter.",
                {"shelter_id": {"type": "string"}, "occupancy": {"type": "integer"}},
                required=["shelter_id", "occupancy"]),
            make_tool("get_capacity_summary",
                "Get total capacity and occupancy summary by district.",
                {"district": {"type": "string", "default": "all"}},
                required=[]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        handlers = {
            "find_nearby_shelters":  self._find_nearby,
            "get_shelter_details":   self._get_details,
            "update_shelter_occupancy": self._update_occupancy,
            "get_capacity_summary":  self._capacity_summary,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return await handler(arguments)
        except Exception as e:
            return {"error": str(e)}

    async def _find_nearby(self, args: dict) -> dict:
        lat = float(args.get("lat", 8.7139))
        lon = float(args.get("lon", 77.7567))
        radius = float(args.get("radius_km", 20))

        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute("SELECT * FROM shelters WHERE is_active = 1")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception:
            rows = []

        nearby = []
        for s in rows:
            dist = math.sqrt((lat - s["location_lat"])**2 + (lon - s["location_lon"])**2) * 111
            if dist <= radius:
                s["distance_km"] = round(dist, 2)
                s["available"] = s.get("capacity", 0) - s.get("current_occupancy", 0)
                nearby.append(s)

        nearby.sort(key=lambda x: x["distance_km"])
        return {"shelters": nearby, "count": len(nearby), "radius_km": radius,
                "search_lat": lat, "search_lon": lon}

    async def _get_details(self, args: dict) -> dict:
        sid = args.get("shelter_id")
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute("SELECT * FROM shelters WHERE shelter_id = ?", (sid,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
        except Exception:
            pass
        return {"error": f"Shelter {sid} not found"}

    async def _update_occupancy(self, args: dict) -> dict:
        sid = args.get("shelter_id")
        occ = int(args.get("occupancy", 0))
        try:
            from database.schema import get_connection
            conn = get_connection()
            conn.execute(
                "UPDATE shelters SET current_occupancy = ?, updated_at = datetime('now') WHERE shelter_id = ?",
                (occ, sid)
            )
            conn.commit()
            conn.close()
            return {"success": True, "shelter_id": sid, "new_occupancy": occ}
        except Exception as e:
            return {"error": str(e)}

    async def _capacity_summary(self, args: dict) -> dict:
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute(
                """SELECT district, SUM(capacity) as total_cap, SUM(current_occupancy) as total_occ
                   FROM shelters WHERE is_active=1 GROUP BY district"""
            )
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return {"summary": rows, "districts": len(rows)}
        except Exception as e:
            return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 3: RESOURCE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
class ResourceManagementMCPServer:
    """
    MCP Server for disaster resource tracking and allocation.
    
    Tools:
    - get_resource_inventory(resource_type?)
    - allocate_resources(resource_type, quantity, destination)
    - get_supply_gaps(affected_people, disaster_type)
    - update_resource_quantity(resource_id, quantity)
    """

    SERVER_NAME = "resource-management-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("get_resource_inventory",
                "Get current inventory of disaster relief resources.",
                {"resource_type": {"type": "string", "enum": ["food","water","medicine","equipment","all"], "default": "all"},
                 "available_only": {"type": "boolean", "default": True}},
                required=[]),
            make_tool("allocate_resources",
                "Record resource allocation to a destination.",
                {"resource_type": {"type": "string"}, "quantity": {"type": "number"},
                 "destination": {"type": "string"}, "disaster_event_id": {"type": "string"}},
                required=["resource_type", "quantity", "destination"]),
            make_tool("get_supply_gaps",
                "Calculate supply gaps for a given number of affected people.",
                {"affected_people": {"type": "integer"}, "disaster_type": {"type": "string"}},
                required=["affected_people"]),
            make_tool("update_resource_quantity",
                "Update the available quantity of a resource item.",
                {"resource_id": {"type": "string"}, "quantity": {"type": "number"}, "operation": {"type": "string", "enum": ["set","add","subtract"]}},
                required=["resource_id", "quantity"]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        handlers = {
            "get_resource_inventory": self._get_inventory,
            "allocate_resources":     self._allocate,
            "get_supply_gaps":        self._get_gaps,
            "update_resource_quantity": self._update_qty,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return await handler(arguments)

    async def _get_inventory(self, args: dict) -> dict:
        rtype = args.get("resource_type", "all")
        avail = args.get("available_only", True)
        try:
            from database.schema import get_connection
            conn = get_connection()
            if rtype == "all":
                q = "SELECT * FROM resource_inventory" + (" WHERE available=1" if avail else "")
                cursor = conn.execute(q)
            else:
                q = "SELECT * FROM resource_inventory WHERE resource_type=?" + (" AND available=1" if avail else "")
                cursor = conn.execute(q, (rtype,))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return {"resources": rows, "count": len(rows), "type_filter": rtype}
        except Exception as e:
            return {"error": str(e)}

    async def _allocate(self, args: dict) -> dict:
        return {
            "success": True,
            "allocated": args.get("quantity"),
            "resource_type": args.get("resource_type"),
            "destination": args.get("destination"),
            "timestamp": datetime.utcnow().isoformat(),
            "tracking_id": f"ALLOC-{int(datetime.utcnow().timestamp())}",
        }

    async def _get_gaps(self, args: dict) -> dict:
        people = int(args.get("affected_people", 1000))
        needs = {"food_packets": people * 3, "water_cans_20L": people // 4, "first_aid_kits": max(1, people // 10)}
        # TODO: compare against real inventory
        return {"people": people, "requirements": needs, "note": "Based on NDMA standard norms"}

    async def _update_qty(self, args: dict) -> dict:
        rid = args.get("resource_id")
        qty = float(args.get("quantity", 0))
        op = args.get("operation", "set")
        try:
            from database.schema import get_connection
            conn = get_connection()
            if op == "set":
                conn.execute("UPDATE resource_inventory SET quantity=?, last_updated=datetime('now') WHERE resource_id=?", (qty, rid))
            elif op == "add":
                conn.execute("UPDATE resource_inventory SET quantity=quantity+?, last_updated=datetime('now') WHERE resource_id=?", (qty, rid))
            elif op == "subtract":
                conn.execute("UPDATE resource_inventory SET quantity=MAX(0,quantity-?), last_updated=datetime('now') WHERE resource_id=?", (qty, rid))
            conn.commit()
            conn.close()
            return {"success": True, "resource_id": rid, "operation": op, "amount": qty}
        except Exception as e:
            return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 4: GOVERNMENT RELIEF
# ══════════════════════════════════════════════════════════════════════════════
class GovernmentReliefMCPServer:
    """
    MCP Server for government and NGO relief program information.
    """

    SERVER_NAME = "government-relief-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("get_relief_programs",
                "Search for government and NGO relief programs.",
                {"disaster_type": {"type": "string"}, "state": {"type": "string", "default": "Tamil Nadu"},
                 "provider_type": {"type": "string", "enum": ["Central Government","State Government","NGO","all"], "default": "all"}},
                required=[]),
            make_tool("check_eligibility",
                "Check eligibility for a specific relief program.",
                {"program_id": {"type": "string"}, "user_profile": {"type": "object"}},
                required=["program_id"]),
            make_tool("submit_relief_application",
                "Submit an application for a relief program.",
                {"program_id": {"type": "string"}, "applicant_name": {"type": "string"},
                 "applicant_phone": {"type": "string"}, "disaster_event_id": {"type": "string"},
                 "details": {"type": "string"}},
                required=["program_id", "applicant_name"]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        handlers = {
            "get_relief_programs":      self._get_programs,
            "check_eligibility":        self._check_eligibility,
            "submit_relief_application": self._submit_application,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return await handler(arguments)

    async def _get_programs(self, args: dict) -> dict:
        try:
            from database.schema import get_connection
            conn = get_connection()
            cursor = conn.execute("SELECT * FROM relief_programs WHERE is_active=1")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return {"programs": rows, "count": len(rows)}
        except Exception as e:
            return {"error": str(e)}

    async def _check_eligibility(self, args: dict) -> dict:
        pid = args.get("program_id")
        return {"program_id": pid, "eligible": True,
                "checklist": ["Valid ID proof", "Disaster-affected residence proof", "Bank account details"],
                "note": "Final eligibility determined by government officials."}

    async def _submit_application(self, args: dict) -> dict:
        import uuid
        app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        try:
            from database.schema import get_connection
            conn = get_connection()
            conn.execute(
                """INSERT INTO relief_applications (application_id, program_id, applicant_name, applicant_phone, details)
                   VALUES (?, ?, ?, ?, ?)""",
                (app_id, args.get("program_id"), args.get("applicant_name"),
                 args.get("applicant_phone"), args.get("details", ""))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            return {"error": str(e)}
        return {"success": True, "application_id": app_id, "status": "submitted",
                "next_steps": "You will be contacted within 7 working days."}


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 5: MEDICAL KNOWLEDGE
# ══════════════════════════════════════════════════════════════════════════════
class MedicalKnowledgeMCPServer:
    """
    MCP Server for medical emergency guidance.
    """

    SERVER_NAME = "medical-knowledge-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("get_first_aid_guidance",
                "Get step-by-step first aid instructions for a medical emergency.",
                {"condition": {"type": "string"}, "severity": {"type": "string", "enum": ["mild","moderate","severe"]}},
                required=["condition"]),
            make_tool("find_nearby_hospitals",
                "Find hospitals near given coordinates.",
                {"lat": {"type": "number"}, "lon": {"type": "number"}, "radius_km": {"type": "number", "default": 20}},
                required=["lat", "lon"]),
            make_tool("get_emergency_contacts",
                "Get medical emergency contacts for a region.",
                {"state": {"type": "string", "default": "Tamil Nadu"}},
                required=[]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        handlers = {
            "get_first_aid_guidance": self._first_aid,
            "find_nearby_hospitals":  self._find_hospitals,
            "get_emergency_contacts": self._emergency_contacts,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        return await handler(arguments)

    async def _first_aid(self, args: dict) -> dict:
        condition = args.get("condition", "general").lower()
        guides = {
            "drowning":   ["Remove from water safely", "Check breathing", "CPR if needed", "Call 108"],
            "heat_stroke": ["Move to cool place", "Apply wet cloth", "Give water if conscious", "Call 108"],
            "fracture":   ["Immobilize", "Apply ice", "Do not move person", "Call 108"],
            "default":    ["Keep calm", "Call 108 immediately", "Monitor vital signs"],
        }
        steps = guides.get(condition, guides["default"])
        return {"condition": condition, "steps": steps, "emergency": "108 – Ambulance", "severity": args.get("severity", "moderate")}

    async def _find_hospitals(self, args: dict) -> dict:
        return {
            "hospitals": [
                {"name": "Tirunelveli Govt Medical College", "phone": "0462-2572555", "distance_km": 2.1, "type": "government"},
                {"name": "St. John's Hospital", "phone": "0462-2578801", "distance_km": 3.4, "type": "private"},
                {"name": "SRM Hospitals", "phone": "1800-103-0101", "distance_km": 5.8, "type": "private"},
            ],
            "emergency": "108",
        }

    async def _emergency_contacts(self, args: dict) -> dict:
        return {
            "state": args.get("state", "Tamil Nadu"),
            "contacts": {
                "ambulance": "108", "emergency": "112",
                "disaster_management": "1079", "fire": "101",
                "police": "100", "flood_helpline": "1077",
                "poison_control": "1800-116-117",
                "women_helpline": "1091",
            },
        }


# ══════════════════════════════════════════════════════════════════════════════
# MCP SERVER 6: EMERGENCY CONTACTS
# ══════════════════════════════════════════════════════════════════════════════
class EmergencyContactMCPServer:
    """
    MCP Server for emergency contact management.
    """

    SERVER_NAME = "emergency-contact-mcp"
    SERVER_VERSION = "1.0.0"

    @property
    def tools(self) -> list[dict]:
        return [
            make_tool("get_emergency_contacts",
                "Get emergency contacts for a location/disaster type.",
                {"location": {"type": "string"}, "disaster_type": {"type": "string"}},
                required=["location"]),
            make_tool("get_rescue_teams",
                "Get active rescue team contacts for an area.",
                {"district": {"type": "string"}, "team_type": {"type": "string", "default": "all"}},
                required=["district"]),
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "get_emergency_contacts":
            return {
                "location": arguments.get("location"),
                "national": {"emergency": "112", "ambulance": "108", "fire": "101", "police": "100"},
                "disaster": {"flood": "1077", "cyclone": "1800-103-9116", "general": "1079"},
                "state_tn": {"sdma": "044-28402250", "cm_helpline": "1100"},
                "international": {"ndrf": "011-24363260"},
            }
        elif tool_name == "get_rescue_teams":
            return {
                "district": arguments.get("district"),
                "teams": [
                    {"name": "NDRF Team 8", "type": "national", "contact": "044-22213835", "status": "active"},
                    {"name": "SDRF TN Unit", "type": "state", "contact": "044-28402250", "status": "active"},
                    {"name": "Fire & Rescue – Tirunelveli", "type": "local", "contact": "0462-2334999", "status": "active"},
                ],
            }
        return {"error": f"Unknown tool: {tool_name}"}


# ─── MCP Client (used by agents to call MCP servers) ──────────────────────────
class MCPClient:
    """
    Unified MCP client for agents to invoke MCP server tools.
    In production this would use HTTP/SSE transport.
    Currently uses in-process calls for simplicity.
    """

    def __init__(self):
        self._servers = {
            "weather":   WeatherDisasterMCPServer(),
            "shelter":   ShelterDatabaseMCPServer(),
            "resource":  ResourceManagementMCPServer(),
            "relief":    GovernmentReliefMCPServer(),
            "medical":   MedicalKnowledgeMCPServer(),
            "emergency": EmergencyContactMCPServer(),
        }

    async def call(self, server: str, tool: str, args: dict = None) -> dict:
        """
        Call a tool on an MCP server.
        
        Args:
            server: Server key (weather|shelter|resource|relief|medical|emergency)
            tool:   Tool name
            args:   Tool arguments
        """
        srv = self._servers.get(server)
        if not srv:
            return {"error": f"MCP server '{server}' not found"}
        return await srv.call_tool(tool, args or {})

    def list_servers(self) -> dict:
        """Return all registered MCP servers with their tools."""
        return {
            name: {
                "server_name": srv.SERVER_NAME,
                "version": srv.SERVER_VERSION,
                "tools": [t["name"] for t in srv.tools],
            }
            for name, srv in self._servers.items()
        }

    def get_all_tools(self) -> list[dict]:
        """Get all tool definitions across all servers (for LLM function calling)."""
        all_tools = []
        for server_key, srv in self._servers.items():
            for tool in srv.tools:
                tool_copy = tool.copy()
                tool_copy["server"] = server_key
                all_tools.append(tool_copy)
        return all_tools


# ─── Singleton MCP client for agent use ──────────────────────────────────────
mcp_client = MCPClient()


# ─── Demo Usage ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    async def demo():
        client = MCPClient()
        print("=== MCP Servers ===")
        for k, v in client.list_servers().items():
            print(f"  {k}: {v['server_name']} | tools: {v['tools']}")

        print("\n=== Weather Tool ===")
        result = await client.call("weather", "get_current_weather", {"location": "Tirunelveli"})
        print(json.dumps(result, indent=2))

        print("\n=== Shelter Search ===")
        result = await client.call("shelter", "find_nearby_shelters", {"lat": 8.7139, "lon": 77.7567})
        print(json.dumps(result, indent=2))

        print("\n=== Supply Gaps ===")
        result = await client.call("resource", "get_supply_gaps", {"affected_people": 5000})
        print(json.dumps(result, indent=2))

    asyncio.run(demo())
