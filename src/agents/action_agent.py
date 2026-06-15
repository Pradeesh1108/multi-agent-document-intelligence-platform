"""
Action Agent — Executes business actions based on workflow decisions.

Routes decisions to appropriate LangChain tools and collects results.
All tools are mock implementations designed for easy real integration.
"""

import json
from datetime import datetime, timezone

from src.core.logging import get_logger
from src.schemas.agent_outputs import ActionResult
from src.tools.crm_tool import create_ticket, update_ticket
from src.tools.email_tool import send_notification
from src.tools.validation_tool import validate_document

logger = get_logger(__name__)


class ActionAgent:
    """
    Executes business actions through LangChain tools.

    Maps workflow decisions to concrete tool invocations. Each decision
    type triggers specific tools with data from the workflow state.
    """

    def process(
        self,
        decision: dict | None,
        intent: dict | None,
        extracted_entities: dict | None,
        risk_analysis: dict | None,
        document_id: str = "",
    ) -> dict:
        """
        Execute business actions based on the workflow decision.

        Args:
            decision: WorkflowDecision dict from the Decision Agent.
            intent: Intent classification dict.
            extracted_entities: Extracted entities dict.
            risk_analysis: Risk analysis dict.
            document_id: Document identifier.

        Returns:
            Dict with 'actions' list of ActionResult dicts.
        """
        if not decision:
            logger.warning("[ActionAgent] No decision provided, skipping actions")
            return {"actions": [self._make_result("no_action", "skipped", {"reason": "No decision"})]}

        decision_type = decision.get("decision", "")
        priority = decision.get("priority", "medium")

        logger.info(f"[ActionAgent] Executing actions for decision: {decision_type}")

        actions: list[dict] = []
        entities = (extracted_entities or {}).get("entities", {})
        intent_type = (intent or {}).get("intent", "other")

        try:
            # Route to appropriate action handler
            if decision_type == "escalate_to_crm":
                actions.extend(self._handle_crm_escalation(entities, intent_type, priority, document_id))

            elif decision_type == "create_support_ticket":
                actions.extend(self._handle_support_ticket(entities, intent_type, priority, document_id))

            elif decision_type == "escalate_fraud_alert":
                actions.extend(self._handle_fraud_alert(entities, risk_analysis, document_id))

            elif decision_type == "flag_for_compliance_review":
                actions.extend(self._handle_compliance_flag(entities, document_id))

            elif decision_type == "review_high_value_invoice":
                actions.extend(self._handle_invoice_review(entities, document_id))

            elif decision_type == "process_standard_invoice":
                actions.extend(self._handle_standard_invoice(entities, document_id))

            elif decision_type == "send_rfq_response":
                actions.extend(self._handle_rfq_response(entities, document_id))

            elif decision_type in ("flag_for_manual_review", "request_clarification"):
                actions.extend(self._handle_manual_review(decision, document_id))

            elif decision_type == "log_and_close":
                actions.append(self._make_result(
                    "log_and_close", "success",
                    {"document_id": document_id, "message": "Document logged and closed"},
                ))

            else:
                actions.append(self._make_result(
                    "unknown_action", "skipped",
                    {"decision": decision_type, "message": "No handler for this decision type"},
                ))

        except Exception as e:
            logger.error(f"[ActionAgent] Action execution error: {e}")
            actions.append(self._make_result("error", "failed", {"error": str(e)}))

        logger.info(f"[ActionAgent] Executed {len(actions)} actions")
        return {"actions": actions}

    def _handle_crm_escalation(
        self, entities: dict, intent_type: str, priority: str, document_id: str,
    ) -> list[dict]:
        """Handle CRM escalation — create ticket + send notification."""
        actions = []

        # Create CRM ticket
        ticket_result = create_ticket.invoke({
            "title": entities.get("issue_summary", entities.get("summary", f"Escalation: {document_id}")),
            "description": json.dumps(entities, default=str),
            "priority": priority,
            "customer_name": entities.get("customer_name", "Unknown"),
            "customer_email": entities.get("customer_email", ""),
            "category": intent_type,
        })
        actions.append(self._make_result("crm_ticket_created", "success", ticket_result))

        # Send notification
        notif_result = send_notification.invoke({
            "to": "escalations@company.com",
            "subject": f"[{priority.upper()}] CRM Escalation: {document_id}",
            "body": f"A new {priority} priority escalation has been created.\n"
                    f"Document: {document_id}\nIntent: {intent_type}",
            "priority": "high",
        })
        actions.append(self._make_result("notification_sent", "success", notif_result))

        return actions

    def _handle_support_ticket(
        self, entities: dict, intent_type: str, priority: str, document_id: str,
    ) -> list[dict]:
        """Handle support ticket creation."""
        ticket_result = create_ticket.invoke({
            "title": entities.get("issue_summary", entities.get("summary", f"Support: {document_id}")),
            "description": json.dumps(entities, default=str),
            "priority": priority,
            "customer_name": entities.get("customer_name", "Unknown"),
            "customer_email": entities.get("customer_email", ""),
            "category": "technical",
        })
        return [self._make_result("support_ticket_created", "success", ticket_result)]

    def _handle_fraud_alert(
        self, entities: dict, risk_analysis: dict | None, document_id: str,
    ) -> list[dict]:
        """Handle fraud alert escalation."""
        actions = []

        # Send urgent fraud alert
        risk_info = risk_analysis or {}
        notif_result = send_notification.invoke({
            "to": "fraud-team@company.com",
            "subject": f"[CRITICAL] Fraud Alert: {document_id}",
            "body": (
                f"Fraud risk detected.\n"
                f"Risk Score: {risk_info.get('risk_score', 'N/A')}\n"
                f"Risk Factors: {', '.join(risk_info.get('risk_factors', []))}\n"
                f"Entities: {json.dumps(entities, default=str)}"
            ),
            "priority": "high",
        })
        actions.append(self._make_result("fraud_alert_sent", "success", notif_result))

        # Create tracking ticket
        ticket_result = create_ticket.invoke({
            "title": f"Fraud Investigation: {document_id}",
            "description": f"Risk Score: {risk_info.get('risk_score', 'N/A')}",
            "priority": "critical",
            "customer_name": entities.get("customer_name", "Unknown"),
            "category": "security",
        })
        actions.append(self._make_result("fraud_ticket_created", "success", ticket_result))

        return actions

    def _handle_compliance_flag(self, entities: dict, document_id: str) -> list[dict]:
        """Handle compliance document flagging."""
        notif_result = send_notification.invoke({
            "to": "compliance@company.com",
            "subject": f"Compliance Review Required: {document_id}",
            "body": (
                f"A document has been flagged for compliance review.\n"
                f"Regulatory Keywords: {', '.join(entities.get('regulatory_keywords', []))}\n"
                f"Summary: {entities.get('summary', 'N/A')}"
            ),
            "priority": "high",
        })
        return [self._make_result("compliance_flag_sent", "success", notif_result)]

    def _handle_invoice_review(self, entities: dict, document_id: str) -> list[dict]:
        """Handle high-value invoice review."""
        actions = []

        # Validate the invoice
        validate_result = validate_document.invoke({
            "document_type": "invoice",
            "entities_json": json.dumps(entities, default=str),
            "intent": "invoice",
        })
        actions.append(self._make_result("invoice_validated", "success", validate_result))

        # Notify finance
        notif_result = send_notification.invoke({
            "to": "finance@company.com",
            "subject": f"High-Value Invoice Review: {entities.get('invoice_id', document_id)}",
            "body": (
                f"Invoice requires finance team review.\n"
                f"Amount: {entities.get('amount', 'N/A')}\n"
                f"Vendor: {entities.get('vendor', 'N/A')}"
            ),
            "priority": "high",
        })
        actions.append(self._make_result("finance_notified", "success", notif_result))

        return actions

    def _handle_standard_invoice(self, entities: dict, document_id: str) -> list[dict]:
        """Handle standard invoice processing."""
        validate_result = validate_document.invoke({
            "document_type": "invoice",
            "entities_json": json.dumps(entities, default=str),
            "intent": "invoice",
        })
        return [self._make_result("invoice_processed", "success", validate_result)]

    def _handle_rfq_response(self, entities: dict, document_id: str) -> list[dict]:
        """Handle RFQ response generation."""
        notif_result = send_notification.invoke({
            "to": entities.get("requester_email", "sales@company.com"),
            "subject": f"RE: Request for Quotation - {document_id}",
            "body": (
                f"Thank you for your quotation request.\n"
                f"Products/Services: {', '.join(entities.get('products_services', ['N/A']))}\n"
                f"Our team will prepare a quote within 2 business days."
            ),
        })
        return [self._make_result("rfq_response_sent", "success", notif_result)]

    def _handle_manual_review(self, decision: dict, document_id: str) -> list[dict]:
        """Handle manual review flagging."""
        ticket_result = create_ticket.invoke({
            "title": f"Manual Review Required: {document_id}",
            "description": decision.get("reasoning", "Flagged for manual review"),
            "priority": decision.get("priority", "medium"),
            "customer_name": "System",
            "category": "review",
        })
        return [self._make_result("manual_review_created", "success", ticket_result)]

    @staticmethod
    def _make_result(action_type: str, status: str, details: dict) -> dict:
        """Create an ActionResult dict."""
        return ActionResult(
            action_type=action_type,
            status=status,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ).model_dump()
