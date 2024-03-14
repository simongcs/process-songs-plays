import pytest
from src.tasker.tasker import Tasker, TaskStatus


class TestTask:
    @pytest.fixture(scope="function")
    def mock_tasker(self):
        tasker = Tasker()
        yield tasker
        Tasker.reset_instance()

    @pytest.fixture
    def mock_task(self):
        return {
            "status": TaskStatus.PROCESSING,
            "output_file_path": "./data",
            "task_id": "1",
        }

    def test_new_instance(self):
        tasker = Tasker()
        assert len(tasker.tasks) == 0

    def test_tasker_singleton(self, mock_tasker):
        tasker = Tasker()
        assert tasker == mock_tasker

    def test_set_new_task(self, mock_tasker, mock_task):
        mock_tasker.set_new_task(mock_task)
        task = mock_tasker.get_task(mock_task["task_id"])
        assert task == mock_task

    def test_get_next_task_id(self, mock_tasker):
        task_id = mock_tasker.get_next_task_id()
        assert isinstance(task_id, str)
        assert task_id == "1"

    def test_get_next_task_id_after_create_task(self, mock_tasker, mock_task):
        mock_tasker.set_new_task(mock_task)
        task_id = mock_tasker.get_next_task_id()
        assert task_id == "2"

    def test_change_task_status(self, mock_tasker, mock_task):
        mock_tasker.set_new_task(mock_task)
        mock_tasker.change_task_status(mock_task["task_id"], TaskStatus.FAILED)
        task = mock_tasker.get_task(mock_task["task_id"])
        assert task["status"] == TaskStatus.FAILED
