from flask import Flask, request, send_from_directory
import threading
import os

from src.csv_parser.parser import CsvParser
from src.tasker.tasker import Tasker, TaskStatus


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./data"

# Dictionary to store the processing status and output file path for each task
tasker = Tasker()


@app.route("/process", methods=["POST"])
def process_file():
    if "file" in request.files:
        file = request.files["file"]
        task_id = tasker.get_next_task_id()

        input_file_path = os.path.join(app.config["UPLOAD_FOLDER"],
                                       file.filename)

        output_file_path = os.path.join(
            "data", file.filename.replace(".csv", f"_processed_{task_id}.csv")
        )

        file.save(input_file_path)

        tasker.set_new_task(
            {
                "status": TaskStatus.PROCESSING,
                "output_file_path": output_file_path,
                "task_id": task_id,
            }
        )

        csvParser = CsvParser(input_file_path, output_file_path, tasker)
        threading.Thread(target=csvParser.process_csv, args=(task_id)).start()

        return {"task_id": task_id}
    else:
        return {"error": "No file provided"}, 400


@app.route("/result/<task_id>", methods=["GET"])
def get_result(task_id: str):
    try:
        task = tasker.get_task(task_id)
        if task["status"] == TaskStatus.PROCESSING:
            return {"status": "processing"}
        elif os.path.exists(task["output_file_path"]):
            basepath = os.path.abspath(os.curdir)
            return send_from_directory(
                directory=basepath,
                path=task["output_file_path"], as_attachment=True
            )
        else:
            return {"status": "completed", "error": "File not found"}
    except KeyError:
        return {"error": "Invalid task ID"}, 404
