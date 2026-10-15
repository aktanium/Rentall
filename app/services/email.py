from flask import current_app


def send_email(to: str, subject: str, body: str) -> None:
    """Send an email. Until Flask-Mail is added (Week 9) the message is only logged."""
    current_app.logger.info("EMAIL to=%s subject=%r\n%s", to, subject, body)
