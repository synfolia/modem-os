import json
import os

def replay_trace(filename: str):
    path = os.path.join("core", "research", "trace_store", filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Trace file not found: {path}")

    with open(path, "r") as f:
        trace = json.load(f)

    print(f"\n--- Replaying Research Trace ---")
    print(f"Prompt: {trace.get('prompt')}")
    print(f"Timestamp: {trace.get('timestamp')}\n")

    for i, step in enumerate(trace.get("steps", [])):
        print(f"Step {i+1}: {step}")

    print(f"\nFinal Result: {trace.get('result')}")