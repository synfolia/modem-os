# modem_os/core/ai/symbiosis/detect_drift.py
# Monitor for performance drift
import json
from pathlib import Path

scroll_dir = Path("modem_os/core/scrolls/ai/memory")

for file in scroll_dir.glob("*.bs"):
    with open(file) as f:
        scroll = json.load(f)

    score = scroll.get("attached_model", {}).get("trust_score", 1.0)
    if score < 0.75:
        print(f"[!] Drift detected in '{file.name}' (trust score: {score})")
    else:
        print(f"[✓] Scroll '{file.name}' stable (trust: {score})")