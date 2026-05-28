FROM python:3.10

WORKDIR /app/backend

COPY backend/requirements.txt .

RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/ /app/frontend/

CMD ["python", "app.py"]
