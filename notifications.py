"""Optional transactional mail. No network call unless SMTP is configured."""
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def notify_author(paper, tracking_url, text):
    cfg = current_app.config
    if not cfg.get("SMTP_HOST") or not cfg.get("SMTP_FROM") or not tracking_url:
        return False
    message = EmailMessage()
    message["From"] = cfg["SMTP_FROM"]
    message["To"] = paper["email"]
    message["Subject"] = f"{text['tracking_title']} — {paper['id']}"
    message.set_content(f"{text['reference']}: {paper['id']}\n{paper['sarlavha']}\n\n{tracking_url}")
    try:
        client = smtplib.SMTP_SSL if cfg["SMTP_SSL"] else smtplib.SMTP
        kwargs = {"timeout": 10}
        if cfg["SMTP_SSL"]:
            kwargs["context"] = ssl.create_default_context()
        with client(cfg["SMTP_HOST"], cfg["SMTP_PORT"], **kwargs) as smtp:
            if not cfg["SMTP_SSL"]:
                smtp.starttls(context=ssl.create_default_context())
            if cfg["SMTP_USER"]:
                smtp.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException):
        current_app.logger.exception("Author notification failed for paper %s", paper["id"])
        return False
