import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Настраивает логирование для приложения.

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу для записи логов
    """
    log_format = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (если указан файл)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Настройка уровней для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("faststream").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.CRITICAL)
    logging.getLogger("aiokafka").setLevel(logging.CRITICAL)
    logging.getLogger("kafka.coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("kafka.coordinator.group").setLevel(logging.CRITICAL)
    logging.getLogger("kafka.consumer.subscription_state").setLevel(logging.CRITICAL)
    logging.getLogger("kafka.consumer.group_coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("aiokafka.coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("aiokafka.group_coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("aiokafka.coordinator.group_coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("aiokafka.client").setLevel(logging.CRITICAL)
    logging.getLogger("group_coordinator").setLevel(logging.CRITICAL)
    logging.getLogger("bcrypt").setLevel(logging.ERROR)
    logging.getLogger("passlib").setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """
    Получить logger с указанным именем.

    Args:
        name: Имя логгера

    Returns:
        Настроенный logger
    """
    return logging.getLogger(name)