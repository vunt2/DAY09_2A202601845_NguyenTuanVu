import json
from datetime import datetime
from typing import Dict, Any
from src.config import TRACE_FILE
from src.policy_engine import HandoffPacket

class BaseAgent:
    """
    Base class for specialized Agents in the Multi-Agent Dispute Resolution Pipeline.
    Handles trace logging and standardized step execution interface.
    """

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def log_trace(self, case_id: str, step_num: int, action: str, details: Dict[str, Any]):
        """Logs an agent execution step to trace.jsonl."""
        trace_entry = {
            "case_id": case_id,
            "step": step_num,
            "agent": self.name,
            "role": self.role,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")

    def process(self, packet: HandoffPacket, step_num: int) -> HandoffPacket:
        """Abstract method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement process()")
