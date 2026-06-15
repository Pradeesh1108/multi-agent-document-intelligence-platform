"""
Risk Tool — Automated risk assessment checks.

Performs rule-based risk checks on documents and transactions.
"""

from datetime import datetime, timezone

from langchain_core.tools import tool

from src.core.logging import get_logger

logger = get_logger(__name__)

# High-risk country codes for transaction monitoring
HIGH_RISK_COUNTRIES = {"NG", "GH", "RO", "KP", "IR", "SY", "CU"}
HIGH_RISK_COUNTRY_NAMES = {
    "nigeria", "ghana", "romania", "north korea", "iran", "syria", "cuba"
}


@tool
def perform_risk_checks(
    document_id: str,
    intent: str,
    entities_json: str,
) -> dict:
    """
    Perform automated risk assessment checks on a document.

    Args:
        document_id: Unique document identifier.
        intent: Classified intent of the document.
        entities_json: JSON string of extracted entities.

    Returns:
        Dict with risk check results, flags, and recommendations.
    """
    import json

    try:
        entities = json.loads(entities_json) if isinstance(entities_json, str) else entities_json
    except json.JSONDecodeError:
        entities = {}

    flags: list[str] = []
    risk_score = 0.1  # Baseline risk

    # --- Fraud-related checks ---
    if intent == "fraud_risk":
        risk_score += 0.3
        flags.append("Document classified as potential fraud risk")

    # Check for high-value amounts
    amount = entities.get("amount") or entities.get("total_amount") or entities.get("amount_usd")
    if amount and isinstance(amount, (int, float)):
        if amount > 100000:
            risk_score += 0.25
            flags.append(f"High-value amount detected: ${amount:,.2f}")
        elif amount > 50000:
            risk_score += 0.15
            flags.append(f"Elevated amount: ${amount:,.2f}")

    # Check for high-risk locations
    location_fields = [
        entities.get("location", ""),
        entities.get("origin_country", ""),
        entities.get("country", ""),
    ]
    for loc in location_fields:
        if loc and loc.lower() in HIGH_RISK_COUNTRY_NAMES:
            risk_score += 0.2
            flags.append(f"High-risk location detected: {loc}")

    # Check for missing critical information
    if intent == "invoice":
        critical_fields = ["invoice_id", "vendor", "amount"]
        missing = [f for f in critical_fields if not entities.get(f)]
        if missing:
            risk_score += 0.1 * len(missing)
            flags.append(f"Missing critical fields: {', '.join(missing)}")

    # Check for compliance concerns
    regulatory_kw = entities.get("regulatory_keywords", [])
    if regulatory_kw:
        risk_score += 0.1
        flags.append(f"Regulatory keywords found: {', '.join(regulatory_kw)}")

    # Cap risk score at 1.0
    risk_score = min(risk_score, 1.0)

    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "critical"
    elif risk_score >= 0.5:
        risk_level = "high"
    elif risk_score >= 0.2:
        risk_level = "medium"
    else:
        risk_level = "low"

    logger.info(
        f"[RISK] Document {document_id}: "
        f"score={risk_score:.2f}, level={risk_level}, flags={len(flags)}"
    )

    return {
        "document_id": document_id,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "flags": flags,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
