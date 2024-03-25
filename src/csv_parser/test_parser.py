from unittest.mock import MagicMock, patch
import pytest
import dask.dataframe as dd
from src.csv_parser.parser import CsvParser

INPUT_FILE_PATH = "test/sample.csv"
OUTPUT_FILE_PATH = "./output"
TASK_ID = "1"
CHUNK_SIZE = 100


class TestParser:

    @pytest.fixture
    def mock_csv_parser(self):
        parser = CsvParser(INPUT_FILE_PATH, OUTPUT_FILE_PATH)
        return parser

    @pytest.fixture
    def mock_csv_parser_all_methods(self):
        parser = CsvParser(INPUT_FILE_PATH, OUTPUT_FILE_PATH)
        parser.read_csv_chunks = MagicMock()
        parser.process_chunks = MagicMock()
        parser.save_csv = MagicMock()
        parser.change_task_status = MagicMock()
        return parser

    def test_process_csv(self, mock_csv_parser_all_methods):
        mock_csv_parser_all_methods.process_csv()
        mock_csv_parser_all_methods.read_csv_chunks.assert_called_once_with(
            CsvParser.chunk_size_in_mb(CHUNK_SIZE)
            )

    def test_process_chunks(self, mock_csv_parser):
        chunks = mock_csv_parser.read_csv_chunks(CHUNK_SIZE)
        df = mock_csv_parser.process_chunks(chunks)
        assert isinstance(df, dd.DataFrame)
        assert len(df.columns) == 3  # columns in csv sample

    def test_save_csv(self, mock_csv_parser):
        chunks = mock_csv_parser.read_csv_chunks(CHUNK_SIZE)
        df = mock_csv_parser.process_chunks(chunks)
        with patch.object(df, "to_csv") as mock_to_csv:
            mock_csv_parser.save_csv(df)
            mock_to_csv.assert_called_once_with(
                filename=OUTPUT_FILE_PATH, index=False, single_file=True
                )
