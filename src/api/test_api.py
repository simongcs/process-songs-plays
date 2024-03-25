import os
import tempfile
from unittest.mock import PropertyMock, patch
import pytest

from src.api.api import app

INPUT_FILE_PATH = "test/sample.csv"
OUTPUT_FILE_PATH = "./output"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestProcessFile:

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

    def test_get_result_pending(self, client):
        with patch("src.api.api.celery.AsyncResult") as mock_result:
            mock_result.return_value.state = "PENDING"
            response = client.get("/result/fake_id")
            assert response.status_code == 200
            assert response.json == {"status": "processing"}

    def test_get_result_success(self, client):
        with patch("src.api.api.celery.AsyncResult") as mock_result:
            basepath = os.path.abspath(os.curdir)
            with tempfile.NamedTemporaryFile(
                        dir=basepath, delete=False
                    ) as tmp_file:
                mock_result.return_value.state = "SUCCESS"
                type(mock_result.return_value).result = PropertyMock(
                    return_value={
                        "output_path": os.path.relpath(tmp_file.name, basepath)
                    }
                )
                response = client.get("result/fake_id")
                assert response.status_code == 200
                assert (
                    response.headers["Content-Disposition"]
                    == "attachment; filename={}"
                    .format(os.path.basename(tmp_file.name))
                )

    def test_get_result_success_file_not_found(self, client):
        with patch("src.api.api.celery.AsyncResult") as mock_result:

            mock_result.return_value.state = "SUCCESS"
            type(mock_result.return_value).result = PropertyMock(
                return_value={"output_path": "nonexistent_file.txt"}
            )
            response = client.get("/result/fake_id")
            assert response.status_code == 200
            assert response.json == {
                "status": "completed", "error": "File not found"
                }

    def test_get_result_invalid_task_id(self, client):
        with patch("src.api.api.celery.AsyncResult") as mock_result:
            mock_result.return_value.state = "FAILURE"
            response = client.get("/result/fake_id")
            assert response.status_code == 404
            assert response.json == {"error": "Invalid task ID"}
