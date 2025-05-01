# Replace model on trust loss
# modem_os/core/ai/symbiosis/swap_model.py
import sys
import json
from pathlib import Path
import shutil

def swap_model(scroll_id, version_index=0):
    scroll_path = Path(f"modem_os/core/scrolls/ai/memory/{scroll_id}.bs")

    if not scroll_path.exists():
        print("[!] Scroll not found.")
        return

    with open(scroll_path) as f:
        scroll = json.load(f)

    lineage = scroll["attached_model"].get("lineage", [])
    if not lineage:
        print("[!] No lineage found.")
        return

    new_model_name = lineage[version_index]
    model_src = Path(f"modem_os/core/scrolls/ai/models/weights/{new_model_name}.onnx")
    model_dst = Path(scroll["attached_model"]["model_path"])

    if model_src.exists():
        shutil.copy(model_src, model_dst)
        scroll["attached_model"]["model_name"] = new_model_name
        scroll["attached_model"]["trust_score"] = 1.0
        scroll["attached_model"]["drift_detected"] = False

        with open(scroll_path, "w") as f:
            json.dump(scroll, f, indent=2)

        print(f"[✓] Swapped in model '{new_model_name}' for scroll '{scroll_id}'")
    else:
        print("[!] Model version not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 swap_model.py <scroll_id> [version_index]")
    else:
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        swap_model(sys.argv[1], idx)