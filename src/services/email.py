from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.conf.config import config

from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Contacts API",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send a verification email to the specified recipient with a confirmation link.

    Args:
        email (EmailStr): Recipient's email address to send verification to
        username (str): Recipient's username for personalization
        host (str): Base URL of the application for constructing verification links

    Raises:
        ConnectionErrors: If there is an issue connecting to the email server
        Exception: For any other unexpected errors during email sending

    Example:
        >>> send_email("user@example.com", "john_doe", "https://example.com")
        # Sends verification email to user@example.com with appropriate token
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(f"Email connection error: {err}")
        raise ConnectionErrors(f"Failed to connect to email server: {err}")
    except Exception as err:
        print(f"Unexpected error sending email: {err}")
        raise Exception(f"Failed to send email: {err}")
