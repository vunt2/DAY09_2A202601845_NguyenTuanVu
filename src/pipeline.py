import json
import time
from pathlib import Path
from typing import Dict, Any, List
from src.config import (
    INPUT_DIR, OUTPUT_DIR, TRACE_FILE, METADATA_FILE, LOGGING_DIR,
    MODEL_NAME, MAX_PARAMETER_SIZE, FRAMEWORK, ensure_directories
)
from src.data_loader import DataLoader
from src.llm_client import LLMClient
from src.agents import (
    CoordinatorAgent, OrderSellerAgent, PaymentAgent,
    DeliveryAgent, PolicyAgent, VerifierAgent
)

class DisputeResolutionPipeline:
    """
    Multi-Agent Orchestrator pipeline controlling step-by-step Handoff Flow
    among 6 agents, writing trace.jsonl and output JSON files.
    """

    def __init__(self):
        ensure_directories()
        self.data_loader = DataLoader()
        self.coordinator = CoordinatorAgent()
        self.order_seller = OrderSellerAgent(self.data_loader)
        self.payment = PaymentAgent(self.data_loader)
        self.delivery = DeliveryAgent(self.data_loader)
        self.policy = PolicyAgent()
        self.verifier = VerifierAgent(self.data_loader)

    def run_case_data(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Coordinator Agent
        packet = self.coordinator.initialize_case(case_data)

        # Step 2: Order & Seller Agent
        packet = self.order_seller.process(packet, step_num=2)

        # Step 3: Payment Agent
        packet = self.payment.process(packet, step_num=3)

        # Step 4: Delivery Agent
        packet = self.delivery.process(packet, step_num=4)

        # Step 5: Policy Agent
        packet = self.policy.process(packet, step_num=5)

        # Step 6: Verifier Agent
        packet = self.verifier.process(packet, step_num=6)

        # Format output JSON
        output_json = self.verifier.format_output_json(packet)
        return output_json

    def run_all_cases(self) -> List[Path]:
        start_time = time.time()

        api_active = LLMClient.is_api_key_set()
        mode_str = "OPENROUTER_LLM_API" if api_active else "NATIVE_RULE_ENGINE"
        print(f"\n=======================================================")
        if api_active:
            print(f" ONLINE MODE: OpenRouter LLM API active with model [{MODEL_NAME}]")
        else:
            print(f" OFFLINE MODE: Running Native Grounded Multi-Agent Engine (No API Key)")
        print(f"=======================================================\n")

        # Clear trace.jsonl for fresh execution trace
        if TRACE_FILE.exists():
            TRACE_FILE.unlink()

        input_files = sorted(INPUT_DIR.glob("EC_*.json"))
        output_files = []

        for infile in input_files:
            with open(infile, "r", encoding="utf-8") as f:
                case_data = json.load(f)

            out_data = self.run_case_data(case_data)
            case_id = case_data.get("case_id", infile.stem)

            out_file = OUTPUT_DIR / f"{case_id}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=2)

            output_files.append(out_file)

        elapsed = time.time() - start_time

        # Generate metadata.json at root and logging/
        metadata = {
            "cohort": "K3",
            "policy_version": "EC_POLICY_V1",
            "model": MODEL_NAME,
            "parameter_size": MAX_PARAMETER_SIZE,
            "execution_mode": mode_str,
            "api_key_present": api_active,
            "framework": FRAMEWORK,
            "runtime_seconds": round(elapsed, 4),
            "processed_cases": len(output_files)
        }

        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logging_meta = LOGGING_DIR / "metadata.json"
        with open(logging_meta, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return output_files

if __name__ == "__main__":
    pipeline = DisputeResolutionPipeline()
    print("Running Multi-Agent Dispute Resolution Pipeline...")
    results = pipeline.run_all_cases()
    print(f"\nPipeline finished! Output generated for {len(results)} cases.")
