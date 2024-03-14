## API Documentation

### 1. POST /process

This endpoint receives a file and returns a JSON object containing a task ID.

#### Request

- Method: POST
- Endpoint: `/process`
- Body: 
  - Type: `multipart/form-data`
  - Content: A file to be processed

#### Response

- Success:
  - Status Code: 200
  - Content-Type: `application/json`
  - Body:
    ```json
    {
        "task_id": "<task_id>"
    }
    ```

- Error:
  - Status Code: 400
  - Content-Type: `application/json`
  - Body:
    ```json
    {
        "error": "No file provided"
    }
    ```

### 2. GET /result/{task_id}

This endpoint returns a CSV file containing the result of the processing task associated with the provided task ID.

#### Request

- Method: GET
- Endpoint: `/result/{task_id}`
- URL Parameters:
  - `task_id`: The unique identifier of the processing task

#### Response


- Success:
  - Status Code: 200
  - Content-Type: `application/json`
  - Body:
    ```json
    {
        "status": "processing"
    }
    ```

- Success:
  - Status Code: 200
  - Content-Type: `text/csv`
  - Body: A CSV file containing the result of the processing task

- Error:
  - Status Code: 404
  - Content-Type: `application/json`
  - Body:
    ```json
    {
        "error": "Invalid task ID"
    }
    ```
