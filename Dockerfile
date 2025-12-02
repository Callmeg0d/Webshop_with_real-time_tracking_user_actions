FROM python:3.12-slim

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction

COPY . .

CMD ["gunicorn", "app.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]