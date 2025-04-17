class TaskQueue:
    def __init__(self):
        self.queue = []
        self.counter = 0

    def add_task(self, prompt):
        self.counter += 1
        task_id = f"task-{self.counter}"
        self.queue.append(task_id)
        return task_id
