"""
Email Tool — Mock email notification integration.

Simulates sending email notifications. Can be replaced with
real SMTP or email service (SendGrid, SES, etc.) integration.
"""

import uuid
from datetime import datetime, timezone

from langchain_core.tools import tool

from src.core.logging import get_logger

logger = get_logger(__name__)


@tool
def send_notification(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    priority: str = "normal",
) -> dict:
    """
    Send an email notification.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.
        cc: Optional CC recipients (comma-separated).
        priority: Email priority (low, normal, high).

    Returns:
        Dict with email sending details.
    """
    message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"

    logger.info(
        f"[EMAIL] Sent notification {message_id}: "
        f"to={to}, subject='{subject}', priority={priority}"
    )

    return {
        "message_id": message_id,
        "to": to,
        "cc": cc,
        "subject": subject,
        "body_preview": body[:200] + ("..." if len(body) > 200 else ""),
        "priority": priority,
        "status": "sent",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
