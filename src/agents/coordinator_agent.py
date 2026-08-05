from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.policy_engine import HandoffPacket
from src.llm_client import LLMClient

class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent: Receives customer dispute case, initializes HandoffPacket,
    invokes OpenRouter LLM API to analyze customer intent, logs trace, and dispatches to Domain Agents.
    """

    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            role="Executive Orchestrator & Case Dispatcher"
        )

    def initialize_case(self, case_json: Dict[str, Any]) -> HandoffPacket:
        case_id = case_json.get("case_id", "EC_UNKNOWN")
        opened_at = case_json.get("opened_at", "")
        policy_version = case_json.get("policy_version", "EC_POLICY_V1")
        
        req = case_json.get("customer_request", {})
        claimed_order_id = req.get("claimed_order_id", "")
        customer_msg = req.get("message", "")
        
        packet = HandoffPacket(
            case_id=case_id,
            opened_at=opened_at,
            claimed_order_id=claimed_order_id,
            customer_message=customer_msg,
            policy_version=policy_version
        )
        
        # Real OpenRouter LLM API call if API key is present
        llm_response = None
        if LLMClient.is_api_key_set():
            prompt = f"Analyze customer dispute intent for Case {case_id}, Order {claimed_order_id}: '{customer_msg}'."
            sys_prompt = "You are CoordinatorAgent. Analyze customer request intent for e-commerce dispute resolution."
            llm_response = LLMClient.call_openrouter(prompt=prompt, system_prompt=sys_prompt)
        
        self.log_trace(
            case_id=case_id,
            step_num=1,
            action="INIT_HANDOFF_PACKET",
            details={
                "claimed_order_id": claimed_order_id,
                "opened_at": opened_at,
                "policy_version": policy_version,
                "llm_api_called": LLMClient.is_api_key_set(),
                "llm_status": llm_response.get("status") if llm_response else "skipped"
            }
        )
        
        return packet

    def process(self, packet: HandoffPacket, step_num: int = 1) -> HandoffPacket:
        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="COORDINATE_HANDOFF",
            details={"claimed_order_id": packet.claimed_order_id}
        )
        return packet
