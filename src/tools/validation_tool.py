"""
Validation Tool — Document validation checks.

Performs completeness and integrity validation on processed documents.
"""

from datetime import datetime, timezone

from langchain_core.tools import tool

from src.core.logging import get_logger

logger = get_logger(__name__)


@tool
def validate_document(
    document_type: str,
    entities_json: str,
    intent: str = "",
) -> dict:
    """
    Validate a processed document for completeness and integrity.

    Args:
        document_type: Type of document (invoice, complaint, rfq, etc.).
        entities_json: JSON string of extracted entities to validate.
        intent: The classified intent for additional context.

    Returns:
        Dict with validation results including pass/fail and issues found.
    """
    import json

    try:
        entities = json.loads(entities_json) if isinstance(entities_json, str) else entities_json
    except json.JSONDecodeError:
        entities = {}

    issues: list[str] = []
    warnings: list[str] = []

    # Document-type-specific validation rules
    if document_type == "invoice":
        required = ["invoice_id", "vendor", "amount"]
        for field in required:
            if not entities.get(field):
                issues.append(f"Missing required invoice field: {field}")
        if entities.get("amount") and isinstance(entities["amount"], (int, float)):
            if entities["amount"] <= 0:
                issues.append(f"Invalid invoice amount: {entities['amount']}")
            if entities["amount"] > 100000:
                warnings.append(f"High-value invoice: ${entities['amount']:,.2f}")

    elif document_type == "complaint":
        if not entities.get("issue_summary"):
            issues.append("Missing complaint issue summary")
        if not entities.get("customer_name") and not entities.get("customer_email"):
            warnings.append("No customer contact information found")

    elif document_type == "rfq":
        if not entities.get("products_services"):
            issues.append("No products or services specified in RFQ")

    is_valid = len(issues) == 0

    logger.info(
        f"[VALIDATION] Document type={document_type}: "
        f"valid={is_valid}, issues={len(issues)}, warnings={len(warnings)}"
    )

    return {
        "is_valid": is_valid,
        "document_type": document_type,
        "issues": issues,
        "warnings": warnings,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
