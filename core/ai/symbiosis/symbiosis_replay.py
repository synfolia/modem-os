 # Replay scroll w/ embedded mode
import json
import sys
import onnxruntime as ort
import numpy as np
from pathlib import Path

def run_symbiosis_model(scroll_id):
    scroll_path = Path(f"modem_os/core/scrolls/ai/memory/{scroll_id}.bs")
    if not scroll_path.exists():
        print(f"[!] Scroll file not found: {scroll_path}")
        return

    with open(scroll_path) as f:
        scroll = json.load(f)

    model_path = scroll.get("attached_model", {}).get("model_path")
    if not model_path or not Path(model_path).exists():
        print(f"[!] Model file missing or path invalid: {model_path}")
        return

    print(f"[MAPLE] Running embedded model for scroll '{scroll_id}'...")
    print(f"→ Model: {model_path}")

    # Load ONNX model
    try:
        ort_session = ort.InferenceSession(model_path)
    except Exception as e:
        print(f"[!] Failed to load model: {e}")
        return

    # Dummy input (adjust this to match your model's input shape!)
    dummy_input = np.random.rand(1, 10).astype(np.float32)
    input_name = ort_session.get_inputs()[0].name
    outputs = ort_session.run(None, {input_name: dummy_input})

    print("[✓] Inference complete.")
    print("Output:", outputs)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 symbiosis_replay.py <scroll_id>")
    else:
        run_symbiosis_model(sys.argv[1])