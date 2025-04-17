# MoDEM Main Runner

from core.task_manager.task_queue import TaskQueue
from core.task_manager.task_tracker import TaskTracker
from core.task_manager.task_prioritizer import TaskPrioritizer
from core.task_manager.task_recovery import TaskRecovery

from core.router.sap_mutation.mutate_sap import mutate_sap
from core.router.sap_scoring.score_sap import score_sap
from core.router.branchscript.record_branch import record_branchscript
from core.router.latent_mode.latent_executor import latent_execute

# Task Manager Setup
task_queue = TaskQueue()
task_tracker = TaskTracker()
task_prioritizer = TaskPrioritizer()
task_recovery = TaskRecovery()

# Example: New Task Intake
def new_task(prompt, latent_mode=True):
    task_id = task_queue.add_task(prompt)
    print(f"Task {task_id} queued.")

    # Mutate SAPs
    saps = mutate_sap(prompt)

    # Print SAPs
    for idx, sap in enumerate(saps):
        print(f"Proposal {idx+1}: {sap['title']} - {sap['description'][:50]}...")

    # Score SAPs
    scored_saps = [score_sap(sap) for sap in saps]

    # Pick best SAP
    best_sap = max(scored_saps, key=lambda x: x['composite_score'])

    # Record BranchScript
    record_branchscript(task_id, "SAP", best_sap)

    # Latent execution
    if latent_mode:
        result = latent_execute(best_sap['title'])
    else:
        result = best_sap['title']

    # Record SYRUP and MAPLE
    record_branchscript(task_id, "SYRUP", result)
    record_branchscript(task_id, "MAPLE", result)

    task_tracker.complete_task(task_id)

    return result

# Run
if __name__ == "__main__":
    result = new_task("Draft a cybersecurity incident report.", latent_mode=True)
    print("Final Result:", result)