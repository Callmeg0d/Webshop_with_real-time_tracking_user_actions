import smtplib

from faststream.kafka import KafkaRouter
from pydantic import EmailStr
from shared import get_logger

from app.config import settings
from app.messaging.email_templates import (
    create_order_confirmation_template,
    create_registration_confirmation_template,
)

router = KafkaRouter()
logger = get_logger(__name__)


@router.subscriber("registration_confirmation", group_id="email_service")
async def handle_registration_confirmation(email_to: EmailStr) -> None:
    """Обработчик события регистрации пользователя - отправка email."""
    logger.info(f"Processing registration confirmation email for: {email_to}")
    try:
        msg_context = create_registration_confirmation_template(email_to)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_context)
        
        logger.info(f"Registration confirmation email sent successfully to: {email_to}")
    except Exception as e:
        logger.error(f"Error sending registration confirmation email to {email_to}: {e}", exc_info=True)
        raise


@router.subscriber("order_confirmation", group_id="email_service")
async def handle_order_confirmation(order: dict, email_to: EmailStr) -> None:
    """Обработчик события создания заказа - отправка email."""
    order_id = order.get("order_id", "unknown")
    logger.info(f"Processing order confirmation email for order {order_id}, email: {email_to}")
    try:
        msg_context = create_order_confirmation_template(order, email_to)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_context)
        
        logger.info(f"Order confirmation email sent successfully for order {order_id} to: {email_to}")
    except Exception as e:
        logger.error(f"Error sending order confirmation email for order {order_id} to {email_to}: {e}", exc_info=True)
        raise


