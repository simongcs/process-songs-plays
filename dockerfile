from python:3.12.2-slim-bookworm

WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "main.py"]