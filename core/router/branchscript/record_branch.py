"""
BranchScript Recorder Module

This module provides functionality to record branch scripts for tasks.
"""

import os
import json
from datetime import datetime, timezone

BRANCHSCRIPT_DIR = os.path.join(
    os.path.dirname(__file__), "branch_scripts"
)


def record_branch_script(task_id, stage, data):
    """
    Records a branch script entry for a given task ID and stage.

    Args:
        task_id (str): The ID of the task.
        stage (str): The current stage of the task.
        data (dict): The data to be recorded in the branch script.

    Returns:
        None
    """
    if not os.path.exists(BRANCHSCRIPT_DIR):
        os.makedirs(BRANCHSCRIPT_DIR, exist_ok=True)

    filename = os.path.join(BRANCHSCRIPT_DIR, f"{task_id}.json")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            branch_script = json.load(f)
    else:
        branch_script = {
            "task_id": task_id,
            "history": []
        }

    branch_script["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "data": data
    })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(branch_script, f, indent=2)

    print(f"Recording Branch Script for Task {task_id}, Stage: {stage}")


def record_branch_script_entry(task_id, stage, data):
    """
    Wrapper function to record a branch script for a given task ID and stage.

    Args:
        task_id (str): The ID of the task.
        stage (str): The current stage of the task.
        data (dict): The data to be recorded in the branch script.

    Returns:
        None
    """
    record_branch_script(task_id, stage, data)
    print(f"Branch script recorded for task {task_id} at stage {stage}.")
