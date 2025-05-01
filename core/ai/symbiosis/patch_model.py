# Inject model into scroll
# modem_os/core/ai/symbiosis/patch_model.py
import sys
import shutil
from pathlib import Path
import json

def patch_model(scroll_id, model_path):
    scroll_file = Path(f"modem_os/core/scrolls/ai/memory/{scroll_id}.bs")
    target_model = Path(f"modem_os/core/scrolls/ai/models/weights/{scroll_id}.onnx")

    # Copy model to scroll weight storage
    shutil.copy(model_path, target_model)

    # Update scroll metadata
    if scroll_file.exists():
        with open(scroll_file) as f:
            scroll = json.load(f)
    else:
        scroll = {"scroll_id": scroll_id}

    scroll["attached_model"] = {
        "model_name": Path(model_path).stem,
        "model_path": str(target_model),
        "trust_score": 1.0,
        "drift_detected": False,
        "lineage": []
    }

    with open(scroll_file, "w") as f:
        json.dump(scroll, f, indent=2)

    print(f"[✓] Model '{model_path}' patched into scroll '{scroll_id}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 patch_model.py <scroll_id> <model_path>")
    else:
        patch_model(sys.argv[1], sys.argv[2])