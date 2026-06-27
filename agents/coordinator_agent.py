"""
RescueMind AI – Coordinator Agent
The central orchestrator: classifies requests, delegates to specialized agents,
aggregates outputs, and generates unified disaster response plans.
"""

import json
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

# Intent classification → agent mapping
INTENT_MAP = {
    "shelter":    "shelter",
    "evacuation": "shelter",
    "evacuate":   "shelter",
    "rescue":     "rescue",
    "trapped":    "rescue",
    "medical":    "medical",
    "first aid":  "medical",
    "first_aid":  "medical",
    "drowning":   "medical",
    "hospital":   "medical",
    "injury":     "medical",
    "hurt":       "medical",
    "resource":   "resource",
    "supply":     "resource",
    "food":       "resource",
    "water":      "resource",
    "relief":     "relief",
    "program":    "relief",
    "damage":     "damage",
    "alert":      "alert",
    "warning":    "alert",
    "weather":    "monitoring",
    "flood":      "monitoring",
    "cyclone":    "monitoring",
    "earthquake": "monitoring",
    "wildfire":   "monitoring",
    "heatwave":   "monitoring",
    "plan":       "planning",
    "prepare":    "planning",
    "recover":    "planning",
    "general":    "coordinator",
}


class CoordinatorAgent(BaseAgent):
    """
    Master coordinator that:
    1. Classifies incoming user requests
    2. Delegates to specialized sub-agents
    3. Aggregates and synthesizes their outputs
    4. Produces a unified, actionable response plan
    
    Design: Uses multi-step reasoning with Gemini to understand context,
    then orchestrates the agent pipeline appropriate for the situation.
    """

    def __init__(self):
        super().__init__("Coordinator Agent")
        self._agents: dict = {}  # Lazy-loaded specialized agents

    def _get_agent(self, agent_type: str) -> "BaseAgent":
        """Lazy-load agents to avoid circular imports and reduce startup time."""
        if agent_type not in self._agents:
            if agent_type == "monitoring":
                from agents.monitoring_agent import DisasterMonitoringAgent
                self._agents[agent_type] = DisasterMonitoringAgent()
            elif agent_type == "alert":
                from agents.alert_agent import EmergencyAlertAgent
                self._agents[agent_type] = EmergencyAlertAgent()
            elif agent_type == "shelter":
                from agents.shelter_agent import ShelterEvacuationAgent
                self._agents[agent_type] = ShelterEvacuationAgent()
            elif agent_type == "rescue":
                from agents.rescue_agent import RescueCoordinationAgent
                self._agents[agent_type] = RescueCoordinationAgent()
            elif agent_type == "medical":
                from agents.medical_agent import MedicalAssistanceAgent
                self._agents[agent_type] = MedicalAssistanceAgent()
            elif agent_type == "resource":
                from agents.resource_agent import ResourceAllocationAgent
                self._agents[agent_type] = ResourceAllocationAgent()
            elif agent_type == "damage":
                from agents.damage_agent import DamageAssessmentAgent
                self._agents[agent_type] = DamageAssessmentAgent()
            elif agent_type == "relief":
                from agents.relief_agent import GovernmentReliefAgent
                self._agents[agent_type] = GovernmentReliefAgent()
            elif agent_type == "planning":
                from agents.planning_agent import PlanningAgent
                self._agents[agent_type] = PlanningAgent()
        return self._agents.get(agent_type)

    def _classify_intent(self, query: str) -> list[str]:
        """
        Use Gemini for intent classification, with keyword fallback.
        Returns list of relevant agent types to invoke.
        """
        query_lower = query.lower()

        # Try LLM classification first
        if not self._demo_mode:
            prompt = f"""
You are a disaster response intent classifier.

Classify this user query into one or more categories from this list:
shelter, evacuation, rescue, medical, first_aid, resource, relief, 
damage, alert, weather, flood, cyclone, earthquake, wildfire, plan, prepare, general

Query: "{query}"

Respond ONLY with a valid JSON object:
{{
  "intents": ["category1", "category2"],
  "primary_intent": "category1",
  "urgency": "low|medium|high|critical",
  "location_mentioned": true or false
}}
"""
            result = self._call_gemini(prompt)
            if result and "intents" in result:
                intents = result.get("intents", ["general"])
                return [INTENT_MAP.get(i, "coordinator") for i in intents]

        # Keyword-based fallback
        detected = []
        for keyword, agent in INTENT_MAP.items():
            if keyword.replace("_", " ") in query_lower or keyword in query_lower:
                detected.append(agent)
        return list(set(detected)) if detected else ["coordinator"]

    def _generate_unified_plan(self, query: str, agent_results: list[dict]) -> dict:
        """
        Use Gemini to synthesize multi-agent outputs into a unified plan.
        Falls back to deterministic synthesis in demo mode.
        """
        if not self._demo_mode and self._gemini:
            results_text = json.dumps(agent_results, indent=2, default=str)[:3000]
            prompt = f"""
You are the Coordinator for RescueMind AI, a disaster response system.

User Query: "{query}"

The following specialized agents have provided their assessments:
{results_text}

Synthesize these into a unified, actionable disaster response plan.

Respond ONLY with a valid JSON object:
{{
  "situation_summary": "2-3 sentence overall situation assessment",
  "priority_actions": [
    {{"rank": 1, "action": "...", "urgency": "immediate|within_1hr|within_24hr", "owner": "citizen|responder|government"}},
    {{"rank": 2, "action": "...", "urgency": "...", "owner": "..."}}
  ],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "overall_risk_level": "low|moderate|high|critical",
  "confidence": 0.85,
  "key_contacts": ["Emergency: 112", "Flood Helpline: 1077"],
  "next_steps": "What the user should do in the next 30 minutes"
}}
"""
            result = self._call_gemini(prompt)
            if result:
                return result

        # Demo/fallback synthesis
        return self._demo_synthesis(query, agent_results)

    def _demo_synthesis(self, query: str, agent_results: list[dict]) -> dict:
        """Demo mode: generate realistic synthesis without LLM."""
        query_lower = query.lower()

        # Check if any sub-agent returned high/critical risk
        sub_risks = [r.get("risk_level", "low") for r in agent_results]
        has_critical_sub = any(r in ("critical", "extreme") for r in sub_risks)
        has_high_sub = any(r in ("high",) for r in sub_risks)

        # Check if rescue/trapped context with high severity
        is_rescue = any(w in query_lower for w in ["rescue", "trapped", "help", "emergency"])
        has_injuries = any("injur" in str(r.get("content", "")).lower() or
                          r.get("content", {}).get("vulnerability_flags", {}).get("injured") or
                          r.get("content", {}).get("vulnerability_flags", {}).get("elderly")
                          for r in agent_results)

        if "flood" in query_lower:
            risk = "high"
            actions = [
                {"rank": 1, "action": "Move to higher ground immediately", "urgency": "immediate", "owner": "citizen"},
                {"rank": 2, "action": "Contact local emergency services", "urgency": "immediate", "owner": "citizen"},
                {"rank": 3, "action": "Evacuate to nearest designated shelter", "urgency": "within_1hr", "owner": "citizen"},
                {"rank": 4, "action": "Deploy rescue boats to affected areas", "urgency": "immediate", "owner": "responder"},
            ]
            summary = ("Active flooding detected in low-lying areas. River levels are above danger mark. "
                      "Immediate evacuation of flood-prone zones is recommended.")
        elif "cyclone" in query_lower:
            risk = "critical"
            actions = [
                {"rank": 1, "action": "Seek shelter in a strong building immediately", "urgency": "immediate", "owner": "citizen"},
                {"rank": 2, "action": "Stay away from windows and doors", "urgency": "immediate", "owner": "citizen"},
                {"rank": 3, "action": "Do not venture out until all-clear signal", "urgency": "within_24hr", "owner": "citizen"},
            ]
            summary = ("Cyclone warning in effect. Strong winds and heavy rainfall expected. "
                      "Coastal areas face highest risk. All residents should shelter in place.")
        elif "medical" in query_lower or "first aid" in query_lower:
            risk = "moderate"
            actions = [
                {"rank": 1, "action": "Call 108 (Ambulance) or 112 (Emergency)", "urgency": "immediate", "owner": "citizen"},
                {"rank": 2, "action": "Provide first aid if trained", "urgency": "immediate", "owner": "citizen"},
                {"rank": 3, "action": "Proceed to nearest hospital", "urgency": "within_1hr", "owner": "citizen"},
            ]
            summary = "Medical assistance requested. Emergency services have been notified. First aid guidance provided."
        else:
            risk = "moderate"
            actions = [
                {"rank": 1, "action": "Stay informed via official channels", "urgency": "within_1hr", "owner": "citizen"},
                {"rank": 2, "action": "Prepare emergency kit (water, food, documents)", "urgency": "within_24hr", "owner": "citizen"},
                {"rank": 3, "action": "Identify nearest shelter location", "urgency": "within_24hr", "owner": "citizen"},
            ]
            summary = ("Disaster preparedness assessment completed. "
                      "No immediate critical threat detected. Recommend standard preparedness measures.")

        recommendations = [r["recommendation"] for r in agent_results if r.get("recommendation")]
        if not recommendations:
            recommendations = [a["action"] for a in actions[:3]]

        # Propagate higher risk from sub-agents or rescue context
        if has_critical_sub or (is_rescue and has_injuries):
            risk = "critical"
        elif has_high_sub or is_rescue:
            risk = max(risk, "high") if risk not in ("critical", "extreme") else risk

        return {
            "situation_summary": summary,
            "priority_actions": actions,
            "recommendations": recommendations,
            "overall_risk_level": risk,
            "confidence": 0.82,
            "key_contacts": [
                "National Emergency: 112",
                "Ambulance: 108",
                "Flood Helpline: 1077",
                "Disaster Management: 1079",
                "Police: 100",
                "Fire: 101",
            ],
            "next_steps": actions[0]["action"] if actions else "Contact emergency services",
        }

    def _execute(self, context: dict) -> AgentResponse:
        """
        Coordinator execution pipeline:
        1. Classify intent
        2. Delegate to relevant agents
        3. Synthesize unified plan
        4. Return explainable response
        """
        query = context.get("query", "")
        location = context.get("location", "")
        disaster_type = context.get("disaster_type", "")

        if not query:
            return AgentResponse(
                agent_name=self.agent_name,
                action="coordinate",
                success=False,
                error="No query provided.",
                recommendation="Please describe your emergency situation.",
            )

        # Step 1: Classify intent
        agent_types = self._classify_intent(query)
        logger.info(f"[Coordinator] Identified agents: {agent_types}")

        # Step 2: Build sub-contexts and collect results
        agent_results = []
        sub_context = {
            "query": query,
            "location": location,
            "disaster_type": disaster_type,
            "session_id": context.get("session_id", ""),
            "user_id": context.get("user_id", ""),
        }

        for agent_type in set(agent_types):
            if agent_type == "coordinator":
                continue
            agent = self._get_agent(agent_type)
            if agent:
                logger.info(f"[Coordinator] Delegating to: {agent.agent_name}")
                result = agent.run(sub_context)
                agent_results.append({
                    "agent": agent.agent_name,
                    "recommendation": result.recommendation,
                    "risk_level": result.risk_level,
                    "confidence": result.confidence,
                    "content": result.content,
                    "alternatives": result.alternatives,
                })

        # Step 3: Synthesize unified plan
        unified = self._generate_unified_plan(query, agent_results)

        # Build the response
        return AgentResponse(
            agent_name=self.agent_name,
            action="coordinate",
            success=True,
            content={
                "unified_plan": unified,
                "agent_results": agent_results,
                "agents_consulted": [r["agent"] for r in agent_results],
                "intent_detected": agent_types,
            },
            recommendation=unified.get("next_steps", "Follow priority actions above."),
            reason=(
                f"Analyzed query across {len(agent_results)} specialized agents. "
                f"Overall risk: {unified.get('overall_risk_level', 'moderate').upper()}. "
                f"Situation: {unified.get('situation_summary', '')[:100]}"
            ),
            data_sources=["Multi-agent synthesis", "Gemini 1.5 Pro", "Disaster database"],
            confidence=unified.get("confidence", 0.80),
            risk_level=unified.get("overall_risk_level", "moderate"),
            alternatives=[a["action"] for a in unified.get("priority_actions", [])[:3]],
        )
