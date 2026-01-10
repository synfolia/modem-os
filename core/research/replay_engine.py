import json
import os


def replay_trace(filename: str):
    """
    Replays a research trace from a specified JSON file.

    This function loads a trace file from a predefined directory structure,
    parses its contents, and prints the details of the trace, including the
    prompt, timestamp, steps, and final result.

    Args:
        filename (str): The name of the trace file to replay.

    Raises:
        FileNotFoundError: If the specified trace file does not exist.

    Example:
        replay_trace("example_trace.json")
    """
    # Security: Sanitize filename to prevent path traversal
    filename = os.path.basename(filename)

    path = os.path.join(
        "scrolls", "r_and_d", "maria_lab", "flare_trials", filename
    )

    if not os.path.exists(path):
        raise FileNotFoundError(f"Trace file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        trace = json.load(f)
        print(f"Loaded trace from {path}")

    print("\n--- Replaying Research Trace ---")
    print(f"Prompt: {trace.get('prompt')}")
    print(f"Timestamp: {trace.get('timestamp')}\n")

    for i, step in enumerate(trace.get("steps", [])):
        print(f"Step {i+1}: {step}")

    print(f"\nFinal Result: {trace.get('result')}")
