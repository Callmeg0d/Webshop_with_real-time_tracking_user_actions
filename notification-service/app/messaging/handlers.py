import smtplib

from faststream.kafka import KafkaRouter
from pydantic import EmailStr

from app.config import settings
from app.messaging.email_templates import (
    create_order_confirmation_template,
    create_registration_confirmation_template,
)

router = KafkaRouter()


@router.subscriber("registration_confirmation", group_id="email_service")
async def handle_registration_confirmation(email_to: EmailStr) -> None:
    """Обработчик события регистрации пользователя - отправка email."""
    msg_context = create_registration_confirmation_template(email_to)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)


@router.subscriber("order_confirmation", group_id="email_service")
async def handle_order_confirmation(order: dict, email_to: EmailStr) -> None:
    """Обработчик события создания заказа - отправка email."""
    msg_context = create_order_confirmation_template(order, email_to)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)


