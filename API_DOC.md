
# API Documentation

## Endpoints

### POST /process

Uploads a CSV file for processing and returns a task ID.

#### Parameters

- **file** (required): The CSV file to be processed.

#### Response

- **200 OK**:
  ```json
  {
    "task_id": "unique_task_id"
  }
  ```

- **400 Bad Request**:
  ```json
  {
    "error": "No file provided"
  }
  ```

#### Example

```bash
curl -X POST -F "file=@path/to/your/file.csv" http://localhost:5000/process
```

### GET /result/{task_id}

Retrieves the result of a processed file using the provided task ID.

#### Parameters

- **task_id** (required): The unique identifier for the task.

#### Response

- **200 OK**: The processed file is returned as a downloadable attachment if the task is completed.

- **200 OK**:
  ```json
  {
    "status": "processing"
  }
  ```
  This response is returned if the task is still processing.

- **200 OK**:
  ```json
  {
    "status": "completed",
    "error": "File not found"
  }
  ```
  This response is returned if the task is completed but the file could not be found.

- **404 Not Found**:
  ```json
  {
    "error": "Invalid task ID"
  }
  ```

#### Example

```bash
curl http://localhost:5000/result/unique_task_id
```
