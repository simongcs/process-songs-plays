from unittest.mock import MagicMock, patch
import pytest
import pandas as pd
from src.csv_parser.parser import CsvParser
from src.tasker.tasker import Tasker, TaskStatus

INPUT_FILE_PATH = "test/sample.csv"
OUTPUT_FILE_PATH = "./output"
TASK_ID = "1"
CHUNK_SIZE = 1024


class TestParser:
    @pytest.fixture(scope="function")
    def mock_tasker(self):
        tasker = Tasker()
        tasker.change_task_status = MagicMock()
        yield tasker
        Tasker.reset_instance()

    @pytest.fixture
    def mock_csv_parser(self, mock_tasker):
        parser = CsvParser(INPUT_FILE_PATH, OUTPUT_FILE_PATH, mock_tasker)
        return parser

    @pytest.fixture
    def mock_csv_parser_all_methods(self, mock_tasker):
        parser = CsvParser(INPUT_FILE_PATH, OUTPUT_FILE_PATH, mock_tasker)
        parser.get_csv_chunks = MagicMock()
        parser.process_chunks = MagicMock()
        parser.save_csv = MagicMock()
        parser.change_task_status = MagicMock()
        return parser

    def test_process_csv(self, mock_csv_parser_all_methods, mock_tasker):
        mock_csv_parser_all_methods.process_csv(TASK_ID)
        mock_csv_parser_all_methods.get_csv_chunks.assert_called_once_with(
            CHUNK_SIZE
        )
        mock_tasker.change_task_status.assert_called_once_with(
            TASK_ID, TaskStatus.COMPLETED)

    def test_get_csv_chunks(self, mock_csv_parser):
        chunks = mock_csv_parser.get_csv_chunks(CHUNK_SIZE)
        first_chunk = next(chunks)
        assert hasattr(chunks, "__iter__") and hasattr(
            chunks, "__next__"
        ), "The result is not an iterator"
        assert isinstance(
            first_chunk, pd.DataFrame), "the chunk is not a dataframe"

    def test_get_csv_chunks_size_one(self, mock_csv_parser):
        chunks = mock_csv_parser.get_csv_chunks(1)
        chunks_size = len([_ for _ in chunks])
        with open("test/sample.csv", "r") as file:
            # we substract 1 because of the header
            filesize = len([_ for _ in file]) - 1
            assert chunks_size == filesize

    def test_process_chunks(self, mock_csv_parser):
        chunks = mock_csv_parser.get_csv_chunks(CHUNK_SIZE)
        df = mock_csv_parser.process_chunks(chunks)
        assert isinstance(df, pd.DataFrame)
        assert len(df.columns) == 3  # columns in csv sample

    def test_save_csv(self, mock_csv_parser):
        chunks = mock_csv_parser.get_csv_chunks(CHUNK_SIZE)
        df = mock_csv_parser.process_chunks(chunks)
        with patch.object(df, "to_csv") as mock_to_csv:
            mock_csv_parser.save_csv(df)
            mock_to_csv.assert_called_once_with(OUTPUT_FILE_PATH, index=False)
