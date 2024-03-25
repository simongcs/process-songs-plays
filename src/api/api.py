from flask import Flask, request, send_from_directory, current_app
import os
from dotenv import load_dotenv
from src.celery.celery_worker import celery_init_app
from src.celery.tasks.process_csv import task_process_csv

load_dotenv()


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./data"

app.config["CELERY_CONFIG"] = {
    "broker_url": os.getenv("BROKER_URL"),
    "result_backend": os.getenv("RESULT_BACKEND"),
}

celery_config = {
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/0",
}

celery = celery_init_app(app)
celery.set_default()


@app.route("/process", methods=["POST"])
def process_file():
    if "file" in request.files:
        file = request.files["file"]
        input_file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], file.filename
        )

        file.save(input_file_path)
        task = task_process_csv.delay(input_file_path, file.filename)

        return {"task_id": task.id}
    else:
        return {"error": "No file provided"}, 400


@app.route("/result/<task_id>", methods=["GET"])
def get_result(task_id: str):
    task = celery.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "processing"}
    elif task.state == "SUCCESS":
        output_file = task.result.get("output_path")
        if output_file and os.path.exists(output_file):
            basepath = os.path.abspath(os.curdir)
            return send_from_directory(
                directory=basepath, path=output_file, as_attachment=True
            )
        else:
            return {"status": "completed", "error": "File not found"}
    else:
        return {"error": "Invalid task ID"}, 404
