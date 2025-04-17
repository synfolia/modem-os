# Task Tracker

class TaskTracker:
    def __init__(self):
        self.tasks = {}

    def complete_task(self, task_id):
        self.tasks[task_id] = "completed"
        print(f"Task {task_id} marked as completed.")
