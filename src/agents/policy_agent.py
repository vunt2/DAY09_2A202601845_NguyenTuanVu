from src.agents.base_agent import BaseAgent
from src.policy_engine import PolicyEngine, HandoffPacket

class PolicyAgent(BaseAgent):
    """
    Policy Agent: Evaluates EC_POLICY_V1 dispute rules in priority order,
    assigns primary issue, root cause, responsible party, refund, and actions.
    """

    def __init__(self):
        super().__init__(
            name="PolicyAgent",
            role="EC_POLICY_V1 Business Rule Executor"
        )

    def process(self, packet: HandoffPacket, step_num: int = 5) -> HandoffPacket:
        # Run PolicyEngine evaluation
        packet = PolicyEngine.evaluate(packet)

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
                "evidence_count": len(packet.evidence_ids)
            }
        )

        return packet
