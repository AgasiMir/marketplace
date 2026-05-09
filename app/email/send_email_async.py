"""Асинхронная версия отправки email для Celery с использованием asyncio."""

import asyncio
import aiosmtplib

from email.message import EmailMessage
from app.tasks.celery_app import celery_instance
from app.config import settings


async def _send_email_async(recipient: str, subject: str, body: str) -> None:
    """Внутренняя асинхронная функция отправки email.

    Args:
        recipient (str): Адрес получателя.
        subject (str): Тема письма.
        body (str): Текст письма.

    Raises:
        aiosmtplib.SMTPException: Если произошла ошибка при отправке.
    """

    admin_email = "admin@marketplace.org"
    message = EmailMessage()
    message["From"] = admin_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        sender=admin_email,
        recipients=[recipient],
        hostname=settings.MailDEV_HOST,
        port=1025,
    )


@celery_instance.task
def send_email_async(recipient: str, subject: str, body: str) -> None:
    """Асинхронная отправка электронного письма через Celery.

    Создает event loop и запускает асинхронную функцию внутри него.

    Args:
        recipient (str): Адрес получателя.
        subject (str): Тема письма.
        body (str): Текст письма.

    Returns:
        None: Функция ничего не возвращает.
    """
    # Создаем и запускаем event loop для асинхронной функции
    asyncio.run(_send_email_async(recipient, subject, body))


# Альтернативный вариант: функция, которая может быть использована
# напрямую в асинхронном контексте. Не рекомендуется, но оставлена на случай
async def send_email_coroutine(recipient: str, subject: str, body: str) -> None:
    """Асинхронная корутина для отправки email.

    Может быть использована напрямую в асинхронном коде:
    asycnio.create_task(send_email_coroutine(recipient, subject, body)) БЕЗ await

    Args:
        recipient (str): Адрес получателя.
        subject (str): Тема письма.
        body (str): Текст письма.
    """
    await _send_email_async(recipient, subject, body)
