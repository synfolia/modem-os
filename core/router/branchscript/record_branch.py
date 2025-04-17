# BranchScript Recorder

import os
import json
from datetime import datetime

BRANCHSCRIPT_DIR = "org/metrics/retrospectives"

def record_branchscript(task_id, stage, data):
    if not os.path.exists(BRANCHSCRIPT_DIR):
        os.makedirs(BRANCHSCRIPT_DIR, exist_ok=True)

    filename = os.path.join(BRANCHSCRIPT_DIR, f"{task_id}.json")

    if os.path.exists(filename):
        with open(filename, "r") as f:
            branchscript = json.load(f)
    else:
        branchscript = {
            "task_id": task_id,
            "history": []
        }

    branchscript["history"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "data": data
    })

    with open(filename, "w") as f:
        json.dump(branchscript, f, indent=2)

    print(f"Recording BranchScript for Task {task_id}, Stage: {stage}")