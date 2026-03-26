FROM python:3.12-slim

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

COPY shared /app/shared

COPY recommendations-service/pyproject.toml recommendations-service/poetry.lock* ./

RUN ln -sfn /app/shared /shared

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-root

COPY recommendations-service/ .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
