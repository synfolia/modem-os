# modemctl/audit.py
from pathlib import Path
import json

def audit_scroll(scroll_path):
    path = Path(scroll_path)
    if not path.exists():
        print("[MAPLE] Scroll not found:", scroll_path)
        return

    with open(path, "r") as f:
        scroll = json.load(f)

    print("\n[MAPLE AUDIT MODE]")
    print("Scroll ID:", scroll.get("scroll_id"))
    print("Status:", scroll.get("status"))
    print("Type:", scroll.get("type"))
    print("Signed By:", scroll.get("signed_by", "N/A"))
    print("Trust Tier:", scroll.get("trust_tier", "unverified"))
    print("Generated At:", scroll.get("timestamp", "unknown"))
    print("Mutation Source:", scroll.get("mutated_from", "original"))
    print("Reward Prediction:", scroll.get("reward_prediction", "?"))
    print("Trust Decay:", scroll.get("trust_decay", "?"))

    if "ontology" in scroll:
        print("\nOntology Mapping:")
        for key, value in scroll["ontology"].items():
            print(f"  {key} → {value}")

    print("\n[✓] Audit complete.")

# Example usage
if __name__ == "__main__":
    audit_scroll("modem-os/core/scrolls/mutations/evolved_policy_001.bs")