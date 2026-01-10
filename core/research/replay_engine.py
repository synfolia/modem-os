import json
import os
from typing import List


DEFAULT_TRACE_DIRS: List[str] = [
    os.path.join("core", "research", "trace_store"),                 # current default
    os.path.join("scrolls", "r_and_d", "maria_lab", "flare_trials"), # legacy
]


def _resolve_trace_path(filename: str) -> str:
    """
    Resolve a trace path from either:
      - an explicit path provided by user, or
      - a bare filename searched in known trace directories.
    """
    # If user passed a path, allow it but still prevent traversal via weird basenames.
    # We treat absolute paths and explicit relative paths (containing /) as "explicit".
    has_path = (os.path.isabs(filename) or (os.sep in filename) or ("/" in filename))

    if has_path:
        candidate = os.path.normpath(filename)
        if os.path.exists(candidate):
            return candidate
        # If explicit path was given and doesn't exist, fall through to try basename in defaults.

    # Security: sanitize to prevent path traversal when searching in default dirs
    base = os.path.basename(filename)

    tried = []
    for d in DEFAULT_TRACE_DIRS:
        candidate = os.path.join(d, base)
        tried.append(candidate)
        if os.path.exists(candidate):
            return candidate

    tried_str = "\n".join(f"  - {p}" for p in tried)
    raise FileNotFoundError(
        f"Trace file not found: {base}\nSearched:\n{tried_str}"
    )


def replay_trace(filename: str):
    """
    Replays a research trace from a specified JSON file.
    """
    path = _resolve_trace_path(filename)

    with open(path, "r", encoding="utf-8") as f:
        trace = json.load(f)

    print(f"Loaded trace from {path}")
    print("\n--- Replaying Research Trace ---")
    print(f"Prompt: {trace.get('prompt')}")
    print(f"Timestamp: {trace.get('timestamp')}\n")

    for i, step in enumerate(trace.get("steps", [])):
        print(f"Step {i+1}: {step}")

    print(f"\nFinal Result: {trace.get('result')}")
