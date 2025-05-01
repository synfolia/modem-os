import os
import json
import requests
from datetime import datetime

TRACE_DIR = "core/research/trace_store"

def run_deep_research(prompt: str):
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "steps": [],
        "result": None
    }

    try:
        response = requests.post(
            "http://localhost:8000/mcp/route",
            json={"prompt": prompt}
        )
        response.raise_for_status()
        data = response.json()

        trace["steps"] = data.get("steps", [])
        trace["result"] = data.get("result", "[No result returned]")

    except Exception as e:
        trace["result"] = f"[Router error: {str(e)}]"

    save_trace(trace)
    return trace["result"]


def save_trace(trace: dict):
    os.makedirs(TRACE_DIR, exist_ok=True)
    timestamp = trace.get("timestamp", datetime.utcnow().isoformat())
    filename = f"replay_{timestamp.replace(':', '-')}.json"
    filepath = os.path.join(TRACE_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(trace, f, indent=2)

    print(f"[+] Trace saved to {filepath}")