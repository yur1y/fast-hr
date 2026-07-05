import logging
import smtplib
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


async def send_application_confirmation(
    email_to: str, application_id: str, job_title: str
) -> None:
    body = (
        f"Hello,\n\n"
        f"Thank you for applying to the {job_title} position. "
        f"Your application ID is {application_id}.\n\n"
        f"We will review your application and get back to you shortly.\n\n"
        f"Best regards,\nTracePilot"
    )
    if not settings.smtp_host or not settings.smtp_from:
        logger.info(
            "email_skipped to=%s reason=no_smtp_config application_id=%s job=%s",
            email_to,
            application_id,
            job_title,
        )
        return None
    try:
        msg = MIMEText(body)
        msg["Subject"] = f"Application Received: {job_title}"
        msg["From"] = settings.smtp_from
        msg["To"] = email_to

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        logger.info(
            "email_sent to=%s application_id=%s job=%s",
            email_to,
            application_id,
            job_title,
        )
    except Exception:
        logger.exception("smtp_send_failed to=%s", email_to)
    return None


async def send_screening_result(
    email_to: str,
    application_id: str,
    job_title: str,
    fit_score: float | None = None,
    confidence: float | None = None,
    failed: bool = False,
) -> None:
    if failed:
        body = (
            f"Hello,\n\n"
            f"We were unable to complete the automated screening for your application "
            f"to the {job_title} position (ID: {application_id}). "
            f"Our team has been notified and will follow up with you.\n\n"
            f"Best regards,\nTracePilot"
        )
        subject = f"Screening Update: {job_title}"
    else:
        body = (
            f"Hello,\n\n"
            f"Your application for the {job_title} position (ID: {application_id}) "
            f"has completed the initial screening stage.\n\n"
            f"Fit score: {fit_score:.0%}\n"
            f"Confidence: {confidence:.0%}\n\n"
            f"If you meet our criteria, we will reach out to schedule the next step.\n\n"
            f"Best regards,\nTracePilot"
        )
        subject = f"Screening Completed: {job_title}"

    if not settings.smtp_host or not settings.smtp_from:
        logger.info(
            "email_skipped to=%s reason=no_smtp_config application_id=%s status=screening_result",
            email_to,
            application_id,
        )
        return None
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = email_to

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        logger.info(
            "email_sent to=%s application_id=%s status=screening_result failed=%s",
            email_to,
            application_id,
            failed,
        )
    except Exception:
        logger.exception("smtp_send_failed to=%s", email_to)
    return None
