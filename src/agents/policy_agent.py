from src.agents.base_agent import BaseAgent
from src.policy_engine import PolicyEngine, HandoffPacket
from src.llm_client import LLMClient

class PolicyAgent(BaseAgent):
    """
    Policy Agent: Evaluates EC_POLICY_V1 dispute rules in priority order,
    invokes OpenRouter LLM API for policy reasoning, assigns primary issue,
    root cause, responsible party, refund, and actions.
    """

    def __init__(self):
        super().__init__(
            name="PolicyAgent",
            role="EC_POLICY_V1 Business Rule Executor"
        )

    def process(self, packet: HandoffPacket, step_num: int = 5) -> HandoffPacket:
        # Run PolicyEngine evaluation
        packet = PolicyEngine.evaluate(packet)

        # Real OpenRouter LLM API call if API key is present
        llm_response = None
        if LLMClient.is_api_key_set():
            prompt = (
                f"Case {packet.case_id} (Order {packet.claimed_order_id}): "
                f"Evaluate EC_POLICY_V1 rule for status '{packet.order_status}', "
                f"payment_total={packet.payment_total_brl}, late_carrier={packet.late_carrier_delivery}, "
                f"seller_late={packet.seller_late_handoff}. Assigned primary_issue: {packet.primary_issue}."
            )
            sys_prompt = "You are PolicyAgent executing EC_POLICY_V1 business rules."
            llm_response = LLMClient.call_openrouter(prompt=prompt, system_prompt=sys_prompt)

        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="EVALUATE_POLICY",
            details={
                "primary_issue": packet.primary_issue,
                "case_status": packet.case_status,
                "confidence": packet.confidence,
                "recommended_refund_brl": packet.recommended_refund_brl,
                "resolution_actions": packet.resolution_actions,
                "evidence_count": len(packet.evidence_ids),
                "llm_api_called": LLMClient.is_api_key_set(),
                "llm_status": llm_response.get("status") if llm_response else "skipped"
            }
        )

        return packet
