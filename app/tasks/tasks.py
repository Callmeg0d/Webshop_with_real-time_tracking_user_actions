import smtplib

from pydantic import EmailStr

from app.config import settings
from app.tasks.celery_app import celery
from app.tasks.email_templates import (
    create_order_confirmation_template,
    create_registration_confirmation_template,
)


@celery.task
def send_order_confirmation_email(
        order: dict,
        email_to: EmailStr
):
    msg_context = create_order_confirmation_template(order, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)


@celery.task
def send_registration_confirmation_email(
        email_to: EmailStr
):
    msg_context = create_registration_confirmation_template(email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_context)