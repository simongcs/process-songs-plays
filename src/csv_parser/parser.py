import dask.dataframe as dd


class CsvParser:
    def __init__(self, input_file_path: str, output_path: str) -> None:
        self.input_file_path = input_file_path
        self.output_path = output_path

    @classmethod
    def chunk_size_in_mb(cls, chunk_size: int):
        return chunk_size * 1024 * 1024

    def process_csv(self, chunk_size: int = 100) -> None:
        chunk_size_mb = self.chunk_size_in_mb(chunk_size)
        df_chunks = self.read_csv_chunks(chunk_size_mb)
        csv_processed_df = self.process_chunks(df_chunks)
        self.save_csv(csv_processed_df)

    def read_csv_chunks(self, chunk_size: int) -> dd.DataFrame:
        return dd.read_csv(self.input_file_path, blocksize=chunk_size)

    def process_chunks(self, df_chunks: dd.DataFrame) -> dd.DataFrame:
        return df_chunks.groupby(
            ["song", "date"]
            )["Number of Plays"].sum().reset_index()

    def save_csv(self, df: dd.DataFrame) -> None:
        df.to_csv(filename=self.output_path, index=False, single_file=True)
