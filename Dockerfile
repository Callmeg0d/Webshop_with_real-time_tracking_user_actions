FROM python:3.12-alpine AS builder

RUN pip install poetry poetry-plugin-export

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Финальный образ
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]