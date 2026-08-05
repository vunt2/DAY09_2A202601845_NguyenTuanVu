from src.agents.base_agent import BaseAgent
from src.data_loader import DataLoader
from src.policy_engine import HandoffPacket

class OrderSellerAgent(BaseAgent):
    """
    Order & Seller Agent: Audits order status, item details, seller handoff deadlines,
    and calculates item total and freight total.
    """

    def __init__(self, data_loader: DataLoader = None):
        super().__init__(
            name="OrderSellerAgent",
            role="Order Status & Seller Handoff Auditor"
        )
        self.data_loader = data_loader or DataLoader()

    def process(self, packet: HandoffPacket, step_num: int = 2) -> HandoffPacket:
        oid = packet.claimed_order_id
        order_record = self.data_loader.get_order(oid)
        
        if not order_record:
            packet.order_exists = False
            self.log_trace(
                case_id=packet.case_id,
                step_num=step_num,
                action="AUDIT_ORDER_SELLER",
                details={"status": "ORDER_NOT_FOUND", "claimed_order_id": oid}
            )
            return packet

        packet.order_exists = True
        packet.order_status = order_record.get("order_status", "")
        packet.purchase_timestamp = order_record.get("order_purchase_timestamp", "")
        packet.delivered_customer_date = order_record.get("order_delivered_customer_date")
        packet.delivered_carrier_date = order_record.get("order_delivered_carrier_date")
        packet.estimated_delivery_date = order_record.get("order_estimated_delivery_date")

        items = self.data_loader.get_items(oid)
        packet.items_data = items
        
        item_sum = 0.0
        freight_sum = 0.0
        seller_late = False
        violating_sellers = []
        
        carr_date = packet.delivered_carrier_date
        
        for item in items:
            p = float(item.get("price", 0.0)) if item.get("price") else 0.0
            f = float(item.get("freight_value", 0.0)) if item.get("freight_value") else 0.0
            item_sum += p
            freight_sum += f
            
            ship_limit = item.get("shipping_limit_date", "")
            sid = item.get("seller_id", "")
            
            # Check seller late handoff rule: order_delivered_carrier_date > shipping_limit_date
            if carr_date and ship_limit and carr_date > ship_limit:
                seller_late = True
                if sid and sid not in violating_sellers:
                    violating_sellers.append(sid)

        packet.item_total_brl = item_sum
        packet.freight_total_brl = freight_sum
        packet.seller_late_handoff = seller_late
        packet.violating_seller_ids = violating_sellers

        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="AUDIT_ORDER_SELLER",
            details={
                "order_status": packet.order_status,
                "item_count": len(items),
                "item_total_brl": round(item_sum, 2),
                "freight_total_brl": round(freight_sum, 2),
                "delivered_carrier_date": carr_date,
                "seller_late_handoff": seller_late,
                "violating_sellers": violating_sellers
            }
        )

        return packet
