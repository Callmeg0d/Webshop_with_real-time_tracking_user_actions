FROM python:3.12-slim

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /app

# Копируем shared модуль перед установкой зависимостей
COPY shared /app/shared

# Копируем файлы зависимостей сервиса
COPY product-service/pyproject.toml product-service/poetry.lock ./

# Устанавливаем зависимости (shared будет установлен как локальный пакет)
RUN poetry install --no-interaction

# Копируем код сервиса
COPY product-service/ .

CMD ["gunicorn", "app.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]

