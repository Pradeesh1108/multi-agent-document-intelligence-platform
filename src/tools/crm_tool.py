"""
CRM Tool — Mock CRM integration for ticket management.

Designed as LangChain tools that can be called by the Action Agent.
Mock implementations that can be swapped for real CRM API integrations.
"""

import uuid
from datetime import datetime, timezone

from langchain_core.tools import tool

from src.core.logging import get_logger

logger = get_logger(__name__)


@tool
def create_ticket(
    title: str,
    description: str,
    priority: str,
    customer_name: str,
    customer_email: str = "",
    category: str = "general",
) -> dict:
    """
    Create a new CRM support ticket.

    Args:
        title: Ticket title/subject.
        description: Detailed description of the issue.
        priority: Priority level (low, medium, high, critical).
        customer_name: Name of the customer.
        customer_email: Email address of the customer.
        category: Ticket category (complaint, billing, technical, etc.).

    Returns:
        Dict with ticket creation details.
    """
    ticket_id = f"CRM-{uuid.uuid4().hex[:8].upper()}"

    logger.info(
        f"[CRM] Created ticket {ticket_id}: "
        f"priority={priority}, category={category}, customer={customer_name}"
    )

    return {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "category": category,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assigned_team": _resolve_team(category, priority),
        "sla_response_hours": _resolve_sla(priority),
    }


@tool
def update_ticket(
    ticket_id: str,
    status: str,
    notes: str = "",
) -> dict:
    """
    Update an existing CRM ticket.

    Args:
        ticket_id: The ticket ID to update.
        status: New status (open, in_progress, resolved, closed).
        notes: Additional notes or resolution details.

    Returns:
        Dict with update confirmation.
    """
    logger.info(f"[CRM] Updated ticket {ticket_id}: status={status}")

    return {
        "ticket_id": ticket_id,
        "status": status,
        "notes": notes,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _resolve_team(category: str, priority: str) -> str:
    """Determine the assigned team based on category and priority."""
    if priority in ("critical", "high"):
        if category in ("complaint", "technical"):
            return "senior_engineering"
        if category == "billing":
            return "finance_escalations"
        return "priority_support"
    return "general_support"


def _resolve_sla(priority: str) -> int:
    """Determine SLA response time in hours."""
    sla_map = {"critical": 1, "high": 4, "medium": 8, "low": 24}
    return sla_map.get(priority, 24)
