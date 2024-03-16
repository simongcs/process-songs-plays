import os
from celery import shared_task
from src.csv_parser.parser import CsvParser


@shared_task(bind=True)
def task_process_csv(self, input_path, filename):
    task_id = self.request.id
    output_path = os.path.join(
        "data", filename.replace(".csv", f"_processed_{task_id}.csv")
    )
    csvParser = CsvParser(input_path, output_path)
    csvParser.process_csv()
    return {"output_path": output_path, "task_id": task_id}
