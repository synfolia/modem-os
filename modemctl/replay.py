#!/usr/bin/env python3
"""
This script replays a stored LSTM policy memory scroll for the Maple-OS modem.
It reads the memory scroll from a predefined path, parses it, and
prints its details.
Usage: Run this script directly to replay the memory scroll.
"""
import json
from pathlib import Path


def replay_memory():
    """
    Replays memory from the LSTM policy store.
    This function reads a memory scroll from a predetermined file path and
    displays its contents, including the policy ID, event sequence,
    and reward prediction.

    Note: The function appears to recursively call itself without a base case,
    which may lead to infinite recursion or a stack overflow error.

    Returns:
        None: This function does not return a value but prints the
        memory contents.
        memory_path = Path(
            "modem-os/core/scrolls/ai/memory/"
            "lstm_policy_store.bs"
        )
    Raises:
        Exception: Any exception that occurs during execution is caught
        and printed.
    """
    memory_path = Path(
        "modem-os/core/scrolls/ai/memory/"
        "lstm_policy_store.bs"
    )
    if not memory_path.exists():
        print("[MAPLE] No memory scroll found.")
        return

    with open(memory_path, encoding="utf-8") as f:
        scroll = json.load(f)

    print("\n[MAPLE] Replaying LSTM Policy Memory Scroll")
    print("Policy ID:", scroll.get("policy_id"))
    print("Event Chain:", " → ".join(scroll.get("event_sequence", [])))
    print("Reward Prediction:", scroll.get("reward_prediction"))
    # Removed recursive call to prevent infinite recursion


if __name__ == "__main__":
    replay_memory()