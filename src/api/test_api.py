import os
import io
import pytest

# from flask import Flask

# from your_module import app, tasker, CsvParser, TaskStatus
# Import your Flask app and other necessary components
from src.api.api import app
from src.tasker.tasker import Tasker, TaskStatus


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestProcessFile:
    def test_process_file_with_file(self, client):
        # Create a sample CSV file to upload
        sample_file_content = "column1,column2\nvalue1,value2"
        sample_file = (io.BytesIO(sample_file_content.encode()), "test.csv")

        # Send a POST request with the file
        data = {"file": sample_file}
        response = client.post(
            "/process", content_type="multipart/form-data", data=data
        )

        # Check the response
        assert response.status_code == 200
        assert "task_id" in response.json

        # Perform any necessary cleanup
        os.remove(os.path.join("data", "test.csv"))

    def test_process_file_without_file(self, client):
        # Send a POST request without a file
        response = client.post("/process")

        # Check the response
        assert response.status_code == 400
        assert response.json == {"error": "No file provided"}


class TestGestResult:
    @pytest.fixture(scope="class")
    def mock_tasker(self):
        tasker = Tasker()
        yield tasker
        Tasker.reset_instance()

    def test_get_result_processing(self, client, mock_tasker):
        # Set up a mock task in the processing state
        task_id = "test_task"
        mock_tasker.set_new_task(
            {
                "status": TaskStatus.PROCESSING,
                "task_id": task_id,
                "output_file_path": "path/to/nonexistent/file.csv",
            }
        )

        response = client.get(f"/result/{task_id}")
        assert response.status_code == 200
        assert response.json == {"status": "processing"}

    def test_get_result_completed(self, client, mock_tasker, tmp_path):
        # Set up a mock task in the completed state with a valid file
        task_id = "test_task_completed"
        filename = "test_output.csv"
        output_file_path = f"test/{filename}"

        mock_tasker.set_new_task(
            {
                "status": TaskStatus.COMPLETED,
                "task_id": task_id,
                "output_file_path": output_file_path,
            }
        )
        with open(output_file_path, 'w'):
            response = client.get(f"/result/{task_id}")
            assert response.status_code == 200
            assert (
                response.headers["Content-Disposition"]
                == f"attachment; filename={filename}"
            )

        # Perform any necessary cleanup
        os.remove(output_file_path)

    def test_get_result_completed_file_not_found(self, client, mock_tasker):
        # Set up a mock task in the completed state with a missing file
        task_id = "test_task_missing_file"
        mock_tasker.set_new_task(
            {
                "status": TaskStatus.COMPLETED,
                "task_id": task_id,
                "output_file_path": "path/to/nonexistent/file.csv",
            }
        )

        response = client.get(f"/result/{task_id}")
        assert response.status_code == 200
        assert response.json == {"status": "completed",
                                 "error": "File not found"}

    def test_get_result_invalid_task_id(self, client):
        # Test with an invalid task ID
        response = client.get("/result/invalid_task_id")
        assert response.status_code == 404
        assert response.json == {"error": "Invalid task ID"}
