from src.agents.base_agent import BaseAgent
from src.data_loader import DataLoader
from src.policy_engine import HandoffPacket

class PaymentAgent(BaseAgent):
    """
    Payment Agent: Reconciles payments, sums payment values, counts installments/rows,
    and detects valid split payments.
    """

    def __init__(self, data_loader: DataLoader = None):
        super().__init__(
            name="PaymentAgent",
            role="Financial Reconciler & Payment Auditor"
        )
        self.data_loader = data_loader or DataLoader()

    def process(self, packet: HandoffPacket, step_num: int = 3) -> HandoffPacket:
        oid = packet.claimed_order_id
        payments = self.data_loader.get_payments(oid)
        
        packet.payments_data = payments
        packet.payment_count = len(payments)
        
        pmt_sum = 0.0
        for pmt in payments:
            val = float(pmt.get("payment_value", 0.0)) if pmt.get("payment_value") else 0.0
            pmt_sum += val

        packet.payment_total_brl = pmt_sum

        # Evaluate valid_split_payment condition:
        # 1. Has at least 2 payment rows (payment_count >= 2)
        # 2. Total payment matches total item + freight within 0.10 BRL tolerance
        total_order_cost = packet.item_total_brl + packet.freight_total_brl
        is_split = (packet.payment_count >= 2)
        matches_cost = (abs(pmt_sum - total_order_cost) <= 0.10) and (total_order_cost > 0)
        
        packet.valid_split_payment_flag = bool(is_split and matches_cost)

        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="RECONCILE_PAYMENTS",
            details={
                "payment_count": packet.payment_count,
                "payment_total_brl": round(pmt_sum, 2),
                "order_total_cost": round(total_order_cost, 2),
                "valid_split_payment_flag": packet.valid_split_payment_flag
            }
        )

        return packet
