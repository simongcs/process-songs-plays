import os
import tempfile
from unittest.mock import MagicMock
import pytest
from src.api.api import app
from src.csv_parser.parser import CsvParser
from src.tasker.tasker import Tasker, TaskStatus


INPUT_FILE_PATH = "test/sample.csv"
OUTPUT_FILE_PATH = "./output"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="class")
def mock_tasker():
    tasker = Tasker()
    yield tasker
    Tasker.reset_instance()


class TestProcessFile:

    @pytest.fixture
    def mock_csv_parser(self, mock_tasker):
        parser = CsvParser(INPUT_FILE_PATH, OUTPUT_FILE_PATH, mock_tasker)
        parser.process_csv = MagicMock()
        return parser

    def test_process_file(self, client):
        # Create a temporary directory to simulate the 'data' folder
        with tempfile.TemporaryDirectory() as tmpdir:
            app.config["UPLOAD_FOLDER"] = tmpdir

            # Prepare a sample file to upload
            sample_file_content = b"Sample content"
            sample_file = tempfile.NamedTemporaryFile(delete=False)
            sample_file.write(sample_file_content)
            sample_file.seek(0)

            # Send a POST request with the file
            response = client.post(
                "/process",
                content_type="multipart/form-data",
                data={"file": (sample_file, "sample.csv")},
            )

            # Check the response
            assert response.status_code == 200
            assert "task_id" in response.json

            # Check if the file was saved correctly
            saved_file_path = os.path.join(tmpdir, "sample.csv")
            assert os.path.exists(saved_file_path)

            # Cleanup
            sample_file.close()
            os.unlink(sample_file.name)

    def test_process_file_without_file(self, client):
        # Send a POST request without a file
        response = client.post("/process")

        # Check the response
        assert response.status_code == 400
        assert response.json == {"error": "No file provided"}


class TestGetResult:

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
