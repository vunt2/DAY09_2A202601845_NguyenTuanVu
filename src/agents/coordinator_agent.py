from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.policy_engine import HandoffPacket

class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent: Receives customer dispute case, initializes HandoffPacket,
    logs initiation trace, and hands off to Domain Agents.
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
        
        self.log_trace(
            case_id=case_id,
            step_num=1,
            action="INIT_HANDOFF_PACKET",
            details={
                "claimed_order_id": claimed_order_id,
                "opened_at": opened_at,
                "policy_version": policy_version
            }
        )
        
        return packet

    def process(self, packet: HandoffPacket, step_num: int = 1) -> HandoffPacket:
        # If passed directly through pipeline process
        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="COORDINATE_HANDOFF",
            details={"claimed_order_id": packet.claimed_order_id}
        )
        return packet
