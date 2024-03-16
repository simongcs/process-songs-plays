from unittest.mock import patch
import pytest
from src.api.api import celery
from celery.contrib.testing.worker import start_worker
from src.celery.tasks.process_csv import task_process_csv
from src.csv_parser.parser import CsvParser


@pytest.fixture(scope="module")
def celery_worker():
    with start_worker(celery, perform_ping_check=False):
        yield


def test_task_process_csv(celery_worker, tmp_path):
    input_path = str(tmp_path / "input.csv")
    filename = "input.csv"

    with open(input_path, "w") as f:
        f.write("test data")

    with patch.object(CsvParser, "process_csv") as mock_process_csv:
        result = task_process_csv.apply(args=[input_path, filename]).get()

        assert "input_processed" in result["output_path"]
        assert "task_id" in result

        mock_process_csv.assert_called_once()
