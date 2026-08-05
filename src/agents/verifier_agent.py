from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.data_loader import DataLoader
from src.policy_engine import HandoffPacket

class VerifierAgent(BaseAgent):
    """
    Verifier Agent: Quality Gate & Grounding Inspector.
    Audits evidence existence against Olist CSVs, schema limits, and output integrity.
    """

    def __init__(self, data_loader: DataLoader = None):
        super().__init__(
            name="VerifierAgent",
            role="Quality Gate & Grounding Check Auditor"
        )
        self.data_loader = data_loader or DataLoader()

    def process(self, packet: HandoffPacket, step_num: int = 6) -> HandoffPacket:
        errors = []
        
        # 1. Grounding check on Evidence IDs
        verified_evidences = []
        for ev in packet.evidence_ids:
            if self.data_loader.verify_evidence_exists(ev):
                verified_evidences.append(ev)
            else:
                errors.append(f"Grounding failed for evidence_id: {ev}")

        packet.evidence_ids = verified_evidences[:10]

        # 2. Entity caps check
        if len(packet.affected_order_ids) > 5:
            packet.affected_order_ids = packet.affected_order_ids[:5]
        if len(packet.affected_item_ids) > 5:
            packet.affected_item_ids = packet.affected_item_ids[:5]
        if len(packet.affected_seller_ids) > 5:
            packet.affected_seller_ids = packet.affected_seller_ids[:5]
        if len(packet.affected_payment_ids) > 5:
            packet.affected_payment_ids = packet.affected_payment_ids[:5]

        # 3. Empty item row rule: if no items, clear item/seller IDs and set item/freight total to 0.0
        if not packet.items_data:
            packet.affected_item_ids = []
            packet.affected_seller_ids = []
            packet.item_total_brl = 0.0
            packet.freight_total_brl = 0.0

        # 4. Financial precision & case_status consistency check
        packet.item_total_brl = round(packet.item_total_brl, 2)
        packet.freight_total_brl = round(packet.freight_total_brl, 2)
        packet.payment_total_brl = round(packet.payment_total_brl, 2)
        packet.recommended_refund_brl = round(packet.recommended_refund_brl, 2)

        if packet.recommended_refund_brl > 0.0:
            packet.case_status = "action_required"
        else:
            packet.case_status = "no_action"

        packet.confidence = max(0.0, min(1.0, round(packet.confidence, 2)))

        # 5. Cap arrays
        packet.ranked_causes = packet.ranked_causes[:3]
        packet.responsible_parties = packet.responsible_parties[:3]
        packet.resolution_actions = packet.resolution_actions[:5]

        packet.is_verified = (len(errors) == 0)
        packet.verification_errors = errors

        self.log_trace(
            case_id=packet.case_id,
            step_num=step_num,
            action="VERIFY_QUALITY_GATE",
            details={
                "is_verified": packet.is_verified,
                "error_count": len(errors),
                "verified_evidence_count": len(packet.evidence_ids),
                "case_status": packet.case_status
            }
        )

        return packet

    def format_output_json(self, packet: HandoffPacket) -> Dict[str, Any]:
        """
        Formats the verified HandoffPacket into the official output JSON schema.
        """
        return {
            "case_id": packet.case_id,
            "assessment": {
                "primary_issue": packet.primary_issue,
                "case_status": packet.case_status,
                "confidence": packet.confidence
            },
            "affected_entities": {
                "order_ids": packet.affected_order_ids,
                "item_ids": packet.affected_item_ids,
                "seller_ids": packet.affected_seller_ids,
                "payment_ids": packet.affected_payment_ids
            },
            "root_cause_analysis": {
                "ranked_causes": packet.ranked_causes,
                "responsible_parties": packet.responsible_parties
            },
            "evidence_ids": packet.evidence_ids,
            "financial_resolution": {
                "currency": "BRL",
                "item_total_brl": packet.item_total_brl,
                "freight_total_brl": packet.freight_total_brl,
                "payment_total_brl": packet.payment_total_brl,
                "recommended_refund_brl": packet.recommended_refund_brl
            },
            "resolution_actions": packet.resolution_actions
        }
