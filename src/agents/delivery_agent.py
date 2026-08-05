from src.agents.base_agent import BaseAgent
from src.data_loader import DataLoader
from src.policy_engine import HandoffPacket

class DeliveryAgent(BaseAgent):
    """
    Delivery Agent: Analyzes actual customer delivery timestamp vs estimated delivery deadline
    to determine if delivery was late or on-time.
    """

    def __init__(self, data_loader: DataLoader = None):
        super().__init__(
            name="DeliveryAgent",
            role="Logistics & Delivery Timeline Analyst"
        )
        self.data_loader = data_loader or DataLoader()

    def process(self, packet: HandoffPacket, step_num: int = 4) -> HandoffPacket:
        deliv_cust = packet.delivered_customer_date
        est_deliv = packet.estimated_delivery_date
        
        is_late = False
        on_time = False

        if deliv_cust and est_deliv:
            if deliv_cust > est_deliv:
                is_late = True
            else:
                on_time = True
        
        packet.late_carrier_delivery = is_late
        packet.delivery_on_time = on_time

        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="ANALYZE_DELIVERY",
            details={
                "delivered_customer_date": deliv_cust,
                "estimated_delivery_date": est_deliv,
                "is_late": is_late,
                "on_time": on_time
            }
        )

        return packet
