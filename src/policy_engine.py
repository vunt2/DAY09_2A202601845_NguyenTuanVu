from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class HandoffPacket:
    case_id: str
    opened_at: str
    claimed_order_id: str
    customer_message: str
    policy_version: str = "EC_POLICY_V1"
    
    # Domain Facts extracted by agents
    order_exists: bool = False
    order_status: str = ""
    purchase_timestamp: str = ""
    delivered_customer_date: Optional[str] = None
    delivered_carrier_date: Optional[str] = None
    estimated_delivery_date: Optional[str] = None
    
    # Items & Payments data
    items_data: List[Dict[str, Any]] = field(default_factory=list)
    payments_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Financial metrics
    item_total_brl: float = 0.0
    freight_total_brl: float = 0.0
    payment_total_brl: float = 0.0
    payment_count: int = 0
    
    # Domain flags
    seller_late_handoff: bool = False
    late_carrier_delivery: bool = False
    delivery_on_time: bool = False
    valid_split_payment_flag: bool = False
    violating_seller_ids: List[str] = field(default_factory=list)
    
    # Final Output Assessment fields
    primary_issue: str = ""
    case_status: str = ""  # "action_required" or "no_action"
    confidence: float = 0.95
    
    affected_order_ids: List[str] = field(default_factory=list)
    affected_item_ids: List[str] = field(default_factory=list)
    affected_seller_ids: List[str] = field(default_factory=list)
    affected_payment_ids: List[str] = field(default_factory=list)
    
    ranked_causes: List[Dict[str, Any]] = field(default_factory=list)
    responsible_parties: List[Dict[str, str]] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    recommended_refund_brl: float = 0.0
    resolution_actions: List[str] = field(default_factory=list)
    
    # Trace & Verification
    agent_traces: List[Dict[str, Any]] = field(default_factory=list)
    is_verified: bool = False
    verification_errors: List[str] = field(default_factory=list)


class PolicyEngine:
    """
    Policy Engine applying EC_POLICY_V1 rules for 6 dispute categories with strict priority.
    """

    @staticmethod
    def evaluate(packet: HandoffPacket) -> HandoffPacket:
        oid = packet.claimed_order_id
        
        # Round financial values to 2 decimal places
        item_total = round(packet.item_total_brl, 2)
        freight_total = round(packet.freight_total_brl, 2)
        payment_total = round(packet.payment_total_brl, 2)
        
        # Collect affected entity IDs (capped at 5 items max)
        affected_order_ids = [oid] if packet.order_exists else []
        
        affected_item_ids = []
        affected_seller_ids = []
        seller_set = set()
        
        for item in packet.items_data:
            item_seq = item.get("order_item_id")
            if item_seq:
                affected_item_ids.append(f"{oid}:{item_seq}")
            sid = item.get("seller_id")
            if sid and sid not in seller_set:
                seller_set.add(sid)
                affected_seller_ids.append(sid)
                
        affected_payment_ids = []
        for pmt in packet.payments_data:
            seq = pmt.get("payment_sequential")
            if seq:
                affected_payment_ids.append(f"{oid}:{seq}")
                
        # Enforce max 5 IDs for affected entities
        affected_order_ids = affected_order_ids[:5]
        affected_item_ids = affected_item_ids[:5]
        affected_seller_ids = affected_seller_ids[:5]
        affected_payment_ids = affected_payment_ids[:5]

        # Evaluate rules in strict priority order (1 to 6)
        
        # Rule 1: canceled_order_paid
        if packet.order_status == "canceled" and payment_total > 0:
            primary_issue = "canceled_order_paid"
            root_cause_code = "ORDER_CANCELED_AFTER_PAYMENT"
            resp_party_type = "platform"
            resp_party_id = "OLIST_PLATFORM"
            refund = payment_total
            action = "issue_full_refund"
            case_status = "action_required"
            confidence = 0.95

        # Rule 2: unavailable_order_paid
        elif packet.order_status == "unavailable" and payment_total > 0:
            primary_issue = "unavailable_order_paid"
            root_cause_code = "ORDER_UNAVAILABLE_AFTER_PAYMENT"
            resp_party_type = "platform"
            resp_party_id = "OLIST_PLATFORM"
            refund = payment_total
            action = "issue_full_refund"
            case_status = "action_required"
            confidence = 0.95

        # Rule 3: late_delivery_seller
        elif packet.late_carrier_delivery and packet.seller_late_handoff:
            primary_issue = "late_delivery_seller"
            root_cause_code = "SELLER_HANDOFF_AFTER_LIMIT"
            resp_party_type = "seller"
            violating_sid = packet.violating_seller_ids[0] if packet.violating_seller_ids else (affected_seller_ids[0] if affected_seller_ids else "UNKNOWN_SELLER")
            resp_party_id = violating_sid
            refund = freight_total
            action = "refund_freight"
            case_status = "action_required"
            confidence = 0.95

        # Rule 4: late_delivery_logistics
        elif packet.late_carrier_delivery and not packet.seller_late_handoff:
            primary_issue = "late_delivery_logistics"
            root_cause_code = "CARRIER_DELIVERED_AFTER_ESTIMATE"
            resp_party_type = "logistics_provider"
            resp_party_id = "LOGISTICS_PROVIDER"
            refund = freight_total
            action = "refund_freight"
            case_status = "action_required"
            confidence = 0.95

        # Rule 5: valid_split_payment
        elif packet.valid_split_payment_flag:
            primary_issue = "valid_split_payment"
            root_cause_code = "MULTIPLE_PAYMENTS_RECONCILED"
            resp_party_type = None
            resp_party_id = None
            refund = 0.0
            action = "explain_valid_split_payment"
            case_status = "no_action"
            confidence = 0.95

        # Rule 6: unsupported_late_claim (default fallback)
        else:
            primary_issue = "unsupported_late_claim"
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            resp_party_type = None
            resp_party_id = None
            refund = 0.0
            action = "reject_late_refund"
            case_status = "no_action"
            confidence = 0.95

        # Build evidence IDs with HIGH PRIORITY to policy & order so they are NEVER truncated
        evidences = []
        evidences.append(f"policy:{root_cause_code}")
        if packet.order_exists:
            evidences.append(f"order:{oid}")
        for i_id in affected_item_ids:
            evidences.append(f"item:{i_id}")
        for p_id in affected_payment_ids:
            evidences.append(f"payment:{p_id}")
        for s_id in affected_seller_ids:
            evidences.append(f"seller:{s_id}")

        # Limit evidence IDs to max 10 while guaranteeing policy:TAG is present
        evidences = list(dict.fromkeys(evidences))[:10]

        # Responsible parties
        resp_parties = []
        if resp_party_type and resp_party_id:
            resp_parties.append({"party_type": resp_party_type, "party_id": resp_party_id})

        # Update packet
        packet.primary_issue = primary_issue
        packet.case_status = case_status
        packet.confidence = round(confidence, 2)
        
        packet.affected_order_ids = affected_order_ids
        packet.affected_item_ids = affected_item_ids
        packet.affected_seller_ids = affected_seller_ids
        packet.affected_payment_ids = affected_payment_ids
        
        packet.ranked_causes = [{"cause_code": root_cause_code, "rank": 1}]
        packet.responsible_parties = resp_parties[:3]
        packet.evidence_ids = evidences
        packet.recommended_refund_brl = round(refund, 2)
        packet.resolution_actions = [action][:5]
        
        return packet
