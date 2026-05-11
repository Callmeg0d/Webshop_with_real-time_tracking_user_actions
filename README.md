### Сервисы

| Сервис | Назначение |
| --- | --- |
| `frontend-service` | API Gateway и сервер HTML-страниц. Проксирует запросы к остальным сервисам. |
| `user-service` | Регистрация, вход, JWT/cookie-аутентификация, профиль пользователя и баланс. |
| `product-service` | Товары, категории, остатки, публикация событий изменения товаров. |
| `cart-service` | Корзина пользователя и синхронизация с заказами через Kafka. |
| `order-service` | Создание заказов и saga-процесс резервирования товара и баланса. |
| `review-service` | Отзывы пользователей о товарах. |
| `recommendations-service` | Рекомендации на базе Qdrant, embeddings и BM25. |
| `analytics-service` | Прием событий трекера, публикация в Kafka, хранение и выборки из ClickHouse. |
| `shared` | Общие зависимости: FastAPI-инфраструктура, логирование, настройки, Kafka, Sentry, Prometheus. |

## Технологии

- Python 3.12
- FastAPI, Uvicorn, Gunicorn
- SQLAlchemy 2, asyncpg, Alembic
- PostgreSQL
- Kafka / FastStream
- ClickHouse
- Qdrant
- Prometheus, Grafana
- Sentry
- Poetry
- Docker, Docker Compose
- pytest, pytest-asyncio, httpx

## Структура проекта

```text
├── analytics-service/
├── cart-service/
├── frontend-service/
├── order-service/
├── product-service/
├── recommendations-service/
├── review-service/
├── user-service/
├── shared/
├── grafana/
└── prometheus/
```

Типовая структура backend-сервиса:

```text
service-name/
├── app/
│   ├── api/              # HTTP endpoints
│   ├── core/             # DI, unit of work, инфраструктурные фабрики
│   ├── domain/           # доменные сущности, интерфейсы, мапперы
│   ├── messaging/        # Kafka broker, handlers, publishers
│   ├── models/           # SQLAlchemy-модели
│   ├── repositories/     # доступ к данным
│   ├── schemas/          # Pydantic-схемы
│   ├── services/         # бизнес-логика
│   └── main.py
├── migrations/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env-example
```

## Быстрый старт

### Настройка окружения

В каждом сервисе есть файл `.env-example`. Перед запуском создайте `.env` для нужного сервиса:

```bash
cp product-service/.env-example product-service/.env
cp user-service/.env-example user-service/.env
cp cart-service/.env-example cart-service/.env
cp order-service/.env-example order-service/.env
cp review-service/.env-example review-service/.env
cp frontend-service/.env-example frontend-service/.env
cp analytics-service/.env-example analytics-service/.env
cp recommendations-service/.env-example recommendations-service/.env
```

### Запуск через Docker Compose

Каждый сервис запускается из своей директории:

```bash
cd product-service
docker compose up --build
```

Аналогично можно запустить остальные сервисы

## Локальная разработка

Установите зависимости для нужного сервиса:

```bash
cd product-service
poetry install
```

Запустите приложение:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Для сервисов с миграциями PostgreSQL примените Alembic:

```bash
poetry run alembic upgrade head
```
После запуска FastAPI-сервиса документация доступна по адресам:

- `http://localhost:<PORT>/docs`
- `http://localhost:<PORT>/redoc`


## Полезные команды

```bash
# Установить зависимости сервиса
poetry install

# Запустить сервис локально
poetry run uvicorn app.main:app --reload

# Применить миграции
poetry run alembic upgrade head

# Запустить тесты
poetry run pytest

# Запустить сервис с инфраструктурой
docker compose up --build

# Остановить compose-стек
docker compose down
```
