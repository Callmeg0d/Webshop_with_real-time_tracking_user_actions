FROM python:3.12-slim

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /app

# Копируем shared модуль перед установкой зависимостей
COPY shared /app/shared

# Копируем файлы зависимостей сервиса
COPY cart-service/pyproject.toml cart-service/poetry.lock ./

RUN ln -s /app/shared /shared

# Устанавливаем зависимости (shared будет установлен как локальный пакет)
RUN poetry install --no-interaction

# Копируем код сервиса
COPY cart-service/ .

CMD ["gunicorn", "app.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]

