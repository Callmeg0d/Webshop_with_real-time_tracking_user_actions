import smtplib

from faststream.kafka import KafkaRouter
from pydantic import EmailStr

from app.config import settings
from app.tasks.email_templates import create_registration_confirmation_template, create_order_confirmation_template

router = KafkaRouter()


@router.subscriber("registration_confirmation")
async def handle_registration_confirmation(email_to: EmailStr):
    msg_context = create_registration_confirmation_template(email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)

@router.subscriber("order_confirmation")
async def handle_order_confirmation(order: dict, email_to: EmailStr):
    msg_context = create_order_confirmation_template(order, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)