class TaskTracker:
    """Tracks the status of tasks in the system."""

    def __init__(self):
        """Initialize the task tracker."""
        self.tasks = {}

    def complete_task(self, task_id):
        """Mark a task as completed."""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            print(f"Task {task_id} marked as completed.")
        else:
            print(f"Task {task_id} not found.")

    def fail_task(self, task_id):
        """Mark a task as failed."""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'failed'
