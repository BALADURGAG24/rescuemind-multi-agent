"""
RescueMind AI – Base Agent
Abstract base class for all specialized agents in the multi-agent system.
Provides: Gemini integration, structured output, logging, explainability.
"""

import json
import time
import uuid
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_FLASH_MODEL,
    MAX_TOKENS, TEMPERATURE, DEMO_MODE
)

logger = logging.getLogger(__name__)


# ─── Agent Response Dataclass ─────────────────────────────────────────────────
@dataclass
class AgentResponse:
    """Structured response from any agent, with explainability built-in."""
    
    # Core content
    agent_name: str
    action: str
    success: bool
    content: dict = field(default_factory=dict)
    
    # Explainability
    recommendation: str = ""
    reason: str = ""
    data_sources: list = field(default_factory=list)
    confidence: float = 0.75
    risk_level: str = "moderate"
    alternatives: list = field(default_factory=list)
    
    # Metadata
    session_id: str = ""
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for storage/transmission."""
        return {
            "agent_name": self.agent_name,
            "action": self.action,
            "success": self.success,
            "content": self.content,
            "recommendation": self.recommendation,
            "reason": self.reason,
            "data_sources": self.data_sources,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "alternatives": self.alternatives,
            "session_id": self.session_id,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "error": self.error,
        }

    def to_explainability_card(self) -> str:
        """
        Generate a human-readable explainability card for every recommendation.
        Every agent output MUST be explainable – this is a core design principle.
        """
        alt_text = "\n".join(f"  • {a}" for a in self.alternatives) if self.alternatives else "  • None available"
        sources_text = ", ".join(self.data_sources) if self.data_sources else "Internal knowledge base"
        confidence_pct = f"{self.confidence * 100:.0f}%"
        
        return (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 **{self.agent_name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 **Recommendation:**\n  {self.recommendation}\n\n"
            f"💡 **Why this was recommended:**\n  {self.reason}\n\n"
            f"📊 **Confidence:** {confidence_pct}  |  ⚠️ **Risk Level:** {self.risk_level.upper()}\n\n"
            f"🗄️ **Data Sources:** {sources_text}\n\n"
            f"🔄 **Alternative Actions:**\n{alt_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )


# ─── Base Agent ───────────────────────────────────────────────────────────────
class BaseAgent(ABC):
    """
    Abstract base class for all RescueMind agents.
    
    All agents share:
    - Gemini model access (with graceful demo-mode fallback)
    - Structured JSON output parsing
    - Database logging
    - Explainability generation
    - Error handling with retry logic
    """

    def __init__(self, agent_name: str, use_flash: bool = False):
        self.agent_name = agent_name
        self.model_name = GEMINI_FLASH_MODEL if use_flash else GEMINI_MODEL
        self._gemini = None
        self._demo_mode = DEMO_MODE
        self._init_gemini()
        logger.info(f"Agent initialized: {agent_name} | model={self.model_name} | demo={self._demo_mode}")

    def _init_gemini(self) -> None:
        """Initialize Google Gemini client with API key."""
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
            logger.warning(f"[{self.agent_name}] No API key – running in demo mode.")
            self._demo_mode = True
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self._gemini = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": TEMPERATURE,
                    "max_output_tokens": MAX_TOKENS,
                    "response_mime_type": "application/json",
                },
            )
            logger.info(f"[{self.agent_name}] Gemini initialized: {self.model_name}")
        except ImportError:
            logger.warning(f"[{self.agent_name}] google-generativeai not installed. Demo mode.")
            self._demo_mode = True
        except Exception as e:
            logger.error(f"[{self.agent_name}] Gemini init failed: {e}. Demo mode.")
            self._demo_mode = True

    def _call_gemini(self, prompt: str, max_retries: int = 2) -> Optional[dict]:
        """
        Call Gemini with structured JSON output.
        Retries on transient failures; returns None on total failure.
        """
        if self._demo_mode or not self._gemini:
            return None   # Caller handles demo fallback

        for attempt in range(max_retries + 1):
            try:
                response = self._gemini.generate_content(prompt)
                raw = response.text.strip()
                # Strip markdown code fences if present
                if raw.startswith("```"):
                    raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
                    raw = raw.rstrip("`").strip()
                return json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"[{self.agent_name}] JSON parse error (attempt {attempt+1}): {e}")
                if attempt == max_retries:
                    return None
            except Exception as e:
                logger.error(f"[{self.agent_name}] Gemini call error (attempt {attempt+1}): {e}")
                if attempt == max_retries:
                    return None
                time.sleep(1.5 ** attempt)   # Exponential backoff

    def _log_to_db(self, action: str, input_summary: str,
                   output_summary: str, confidence: float,
                   duration_ms: int, status: str, user_id: str = "",
                   session_id: str = "") -> None:
        """Log agent invocation to database for audit trail."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from database.schema import get_connection
            conn = get_connection()
            conn.execute(
                """INSERT OR IGNORE INTO agent_logs
                   (log_id, agent_name, action, input_summary, output_summary,
                    confidence, duration_ms, status, user_id, session_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), self.agent_name, action,
                 input_summary[:500], output_summary[:500],
                 confidence, duration_ms, status, user_id, session_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"[{self.agent_name}] DB logging failed: {e}")

    def _save_advisory(self, advisory_type: str, query: str,
                       recommendation: str, confidence: float,
                       data_sources: list, risk_level: str,
                       alternatives: list, user_id: str = "",
                       session_id: str = "") -> None:
        """Save recommendation to advisory history for future reference."""
        try:
            from database.schema import get_connection
            conn = get_connection()
            conn.execute(
                """INSERT OR IGNORE INTO advisory_history
                   (advisory_id, user_id, session_id, query, advisory_type,
                    recommendation, confidence, data_sources, risk_level, alternatives)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), user_id, session_id, query[:500],
                 advisory_type, recommendation[:1000], confidence,
                 json.dumps(data_sources), risk_level, json.dumps(alternatives))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Advisory save failed: {e}")

    def run(self, context: dict) -> AgentResponse:
        """
        Main entry point – wraps _execute with timing and logging.
        
        Args:
            context: Dictionary with task parameters (varies by agent)
        
        Returns:
            AgentResponse with structured output and explainability
        """
        start = time.time()
        session_id = context.get("session_id", str(uuid.uuid4())[:8])
        user_id = context.get("user_id", "anonymous")

        logger.info(f"[{self.agent_name}] Starting | session={session_id}")

        try:
            response = self._execute(context)
            response.session_id = session_id
            response.duration_ms = int((time.time() - start) * 1000)

            self._log_to_db(
                action=response.action,
                input_summary=str(context)[:200],
                output_summary=response.recommendation[:200],
                confidence=response.confidence,
                duration_ms=response.duration_ms,
                status="success" if response.success else "error",
                user_id=user_id,
                session_id=session_id,
            )

            if response.success and response.recommendation:
                self._save_advisory(
                    advisory_type=response.action,
                    query=str(context.get("query", context))[:300],
                    recommendation=response.recommendation,
                    confidence=response.confidence,
                    data_sources=response.data_sources,
                    risk_level=response.risk_level,
                    alternatives=response.alternatives,
                    user_id=user_id,
                    session_id=session_id,
                )

            logger.info(
                f"[{self.agent_name}] Completed in {response.duration_ms}ms | "
                f"confidence={response.confidence:.2f}"
            )
            return response

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.error(f"[{self.agent_name}] Execution error: {e}", exc_info=True)
            self._log_to_db(
                action="error", input_summary=str(context)[:200],
                output_summary=str(e)[:200],
                confidence=0.0, duration_ms=duration_ms,
                status="error", user_id=user_id, session_id=session_id,
            )
            return AgentResponse(
                agent_name=self.agent_name,
                action="error",
                success=False,
                error=str(e),
                recommendation="An error occurred. Please try again.",
            )

    @abstractmethod
    def _execute(self, context: dict) -> AgentResponse:
        """
        Subclasses implement this method with their specific logic.
        Must return an AgentResponse with all explainability fields populated.
        """
        pass


# Import regex needed for _call_gemini
import re
