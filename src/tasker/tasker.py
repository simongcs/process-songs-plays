from enum import Enum


class TaskStatus(Enum):
    FAILED = 0
    PROCESSING = 1
    COMPLETED = 2


class Tasker:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Tasker, cls).__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    def __init__(self) -> None:
        self.tasks: dict = {}

    def get_task(self, task_id: str) -> dict:
        return self.tasks[task_id]

    def set_new_task(self, task: dict) -> None:
        self.tasks[task["task_id"]] = task

    def get_next_task_id(self) -> str:
        return str(len(self.tasks) + 1)

    def change_task_status(self, task_id: str, status: TaskStatus):
        self.tasks[task_id]["status"] = status
