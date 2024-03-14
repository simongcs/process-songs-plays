import pandas as pd
from src.tasker.tasker import Tasker, TaskStatus


class CsvParser:
    def __init__(self, input_file_path: str, output_file_path: str,
                 tasker: Tasker) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.tasker = tasker

    def process_csv(self, task_id, chunk_size: int = 1024) -> None:
        chunks = self.get_csv_chunks(chunk_size)
        csv_processed_df = self.process_chunks(chunks)
        self.save_csv(csv_processed_df)
        self.tasker.change_task_status(task_id, TaskStatus.COMPLETED)

    def get_csv_chunks(self, chunk_size: int):
        return pd.read_csv(self.input_file_path, chunksize=chunk_size)

    def process_chunks(self, chunks) -> pd.DataFrame:
        # Initialize an empty DataFrame to store the aggregated results
        result_df = pd.DataFrame()

        # Process each chunk
        for chunk in chunks:
            # Group by 'song' and 'date' and sum the 'Number of Plays'
            aggregated = (
                chunk.groupby(["song", "date"])["Number of Plays"]
                .sum().reset_index()
            )
            # Append the aggregated results to the result DataFrame
            result_df = pd.concat([result_df, aggregated])

        # Group by 'song' and 'date' again in case there were overlaps
        # between chunks
        return (
            result_df.groupby(["song", "date"])["Number of Plays"]
            .sum().reset_index()
        )

    def save_csv(self, df: pd.DataFrame) -> None:
        # Write the result to the output CSV file
        df.to_csv(self.output_file_path, index=False)
