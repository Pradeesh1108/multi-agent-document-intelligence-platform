"""
Intake Agent — Document normalization and preprocessing.

Responsibilities:
    - Detect file type
    - Validate input is non-empty
    - Normalize content (strip whitespace, parse structures)
    - Convert PDF to text
    - Convert Email to structured content
    - Prepare workflow state
"""

import json
from typing import Any

from src.core.logging import get_logger
from src.schemas.documents import FileType
from src.services.document_parser import parse_email_content, validate_json_content

logger = get_logger(__name__)


class IntakeAgent:
    """
    First agent in the pipeline — normalizes and validates incoming documents.

    Does NOT use LLM calls. This is a deterministic preprocessing step
    that prepares documents for downstream agent processing.
    """

    def process(
        self,
        raw_content: str,
        file_type: str,
    ) -> dict[str, Any]:
        """
        Normalize and validate the raw document content.

        Args:
            raw_content: Raw text content of the document.
            file_type: Detected file type string.

        Returns:
            Dict with normalized_content, metadata, and any errors.
        """
        logger.info(f"[IntakeAgent] Processing document (type: {file_type})")

        if not raw_content.strip():
            logger.warning("[IntakeAgent] Empty content received")
            return {
                "normalized_content": "",
                "metadata": {"intake_status": "failed", "reason": "empty_content"},
                "errors": ["Document content is empty"],
            }

        # Normalize based on file type
        try:
            if file_type == FileType.EMAIL.value:
                return self._normalize_email(raw_content)
            elif file_type == FileType.JSON.value:
                return self._normalize_json(raw_content)
            elif file_type == FileType.PDF.value:
                return self._normalize_pdf(raw_content)
            else:
                return self._normalize_generic(raw_content)
        except Exception as e:
            logger.error(f"[IntakeAgent] Normalization error: {e}")
            return {
                "normalized_content": raw_content.strip(),
                "metadata": {"intake_status": "partial", "error": str(e)},
                "errors": [f"Normalization error: {e}"],
            }

    def _normalize_email(self, content: str) -> dict[str, Any]:
        """Normalize email content by parsing headers and body."""
        parsed = parse_email_content(content)

        # Build normalized representation
        parts = []
        if parsed.get("subject"):
            parts.append(f"Subject: {parsed['subject']}")
        if parsed.get("sender_name") or parsed.get("sender_email"):
            sender = parsed.get("sender_name", "") or parsed.get("sender_email", "")
            parts.append(f"From: {sender}")
        if parsed.get("body"):
            parts.append(f"\n{parsed['body']}")

        normalized = "\n".join(parts)

        logger.info(
            f"[IntakeAgent] Email normalized: subject='{parsed.get('subject', 'N/A')}', "
            f"sender='{parsed.get('sender_email', 'N/A')}'"
        )

        return {
            "normalized_content": normalized,
            "metadata": {
                "intake_status": "success",
                "file_type": "email",
                "email_metadata": parsed,
            },
            "errors": [],
        }

    def _normalize_json(self, content: str) -> dict[str, Any]:
        """Normalize JSON content by validating and pretty-printing."""
        is_valid, parsed_data, error_msg = validate_json_content(content)

        if not is_valid:
            logger.warning(f"[IntakeAgent] Invalid JSON: {error_msg}")
            return {
                "normalized_content": content.strip(),
                "metadata": {
                    "intake_status": "partial",
                    "file_type": "json",
                    "json_valid": False,
                    "json_error": error_msg,
                },
                "errors": [f"Invalid JSON: {error_msg}"],
            }

        normalized = json.dumps(parsed_data, indent=2, ensure_ascii=False)

        logger.info(
            f"[IntakeAgent] JSON normalized: "
            f"valid=True, keys={list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'array'}"
        )

        return {
            "normalized_content": normalized,
            "metadata": {
                "intake_status": "success",
                "file_type": "json",
                "json_valid": True,
                "json_keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else [],
            },
            "errors": [],
        }

    def _normalize_pdf(self, content: str) -> dict[str, Any]:
        """Normalize PDF-extracted text content."""
        # Clean up common PDF extraction artifacts
        normalized = content.strip()
        normalized = "\n".join(
            line for line in normalized.split("\n")
            if line.strip()  # Remove empty lines
        )

        word_count = len(normalized.split())
        logger.info(f"[IntakeAgent] PDF text normalized: {word_count} words")

        return {
            "normalized_content": normalized,
            "metadata": {
                "intake_status": "success",
                "file_type": "pdf",
                "word_count": word_count,
            },
            "errors": [],
        }

    def _normalize_generic(self, content: str) -> dict[str, Any]:
        """Normalize generic/unknown content."""
        normalized = content.strip()

        logger.info(f"[IntakeAgent] Generic content normalized: {len(normalized)} chars")

        return {
            "normalized_content": normalized,
            "metadata": {
                "intake_status": "success",
                "file_type": "unknown",
                "char_count": len(normalized),
            },
            "errors": [],
        }
