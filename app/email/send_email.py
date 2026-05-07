from email.message import EmailMessage

import aiosmtplib


async def send_email(recipient: str, subject: str, body: str) -> None:
    """Отправляет электронное письмо через локальный SMTP сервер.

    Используется c background tasks.

    Использует фиксированный адрес отправителя admin@finance-tracker.org
    и SMTP сервер localhost:1025 (например, MailHog для тестирования).

    Args:
        recipient (str): Адрес получателя.
        subject (str): Тема письма.
        body (str): Текст письма.

    Returns:
        None: Функция ничего не возвращает.

    Raises:
        aiosmtplib.SMTPException: Если произошла ошибка при отправке.
    """
    admin_email = "admin@finance-tracker.org"
    message = EmailMessage()
    message["From"] = admin_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        sender=admin_email,
        recipients=[recipient],
        hostname="localhost",
        port=1025,
    )
