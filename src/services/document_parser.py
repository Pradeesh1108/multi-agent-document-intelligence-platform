"""
Document Parser — File type detection and content extraction utilities.

Handles PDF text extraction, email parsing, JSON validation,
and automatic file type detection.
"""

import json
import re
from typing import Any

from src.core.logging import get_logger
from src.schemas.documents import FileType

logger = get_logger(__name__)


def detect_file_type(content: str, filename: str | None = None) -> FileType:
    """
    Detect the file type from content and/or filename.

    Priority:
        1. File extension (if filename provided)
        2. Content-based heuristic detection

    Args:
        content: Raw text content.
        filename: Optional original filename.

    Returns:
        Detected FileType enum value.
    """
    # Extension-based detection
    if filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        ext_map = {
            "pdf": FileType.PDF,
            "json": FileType.JSON,
            "eml": FileType.EMAIL,
            "txt": FileType.UNKNOWN,
        }
        if ext in ext_map:
            detected = ext_map[ext]
            logger.debug(f"File type detected from extension '.{ext}': {detected.value}")
            return detected

    # Content-based heuristic detection
    stripped = content.strip()

    # JSON detection
    if (stripped.startswith("{") and stripped.endswith("}")) or \
       (stripped.startswith("[") and stripped.endswith("]")):
        try:
            json.loads(stripped)
            logger.debug("File type detected from content: JSON")
            return FileType.JSON
        except json.JSONDecodeError:
            pass

    # Email detection — look for email headers
    email_patterns = [
        r"^From:\s*.+",
        r"^Subject:\s*.+",
        r"^To:\s*.+",
        r"^Date:\s*.+",
    ]
    email_header_count = sum(
        1 for pattern in email_patterns
        if re.search(pattern, stripped, re.MULTILINE | re.IGNORECASE)
    )
    if email_header_count >= 2:
        logger.debug("File type detected from content: Email")
        return FileType.EMAIL

    # PDF-extracted text detection
    pdf_indicators = [
        "Invoice Number:", "INV-", "Page ", "Document ID:",
        "CHAPTER ", "Section ", "Table of Contents",
    ]
    pdf_score = sum(1 for ind in pdf_indicators if ind in stripped)
    if pdf_score >= 2:
        logger.debug("File type detected from content: PDF (text)")
        return FileType.PDF

    logger.debug("File type could not be determined, defaulting to UNKNOWN")
    return FileType.UNKNOWN


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text content from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text content.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        ValueError: If the PDF cannot be read.
    """
    import fitz  # PyMuPDF

    logger.info(f"Extracting text from PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        text_parts: list[str] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(text)

        num_pages = len(doc)
        doc.close()

        full_text = "\n".join(text_parts)
        logger.info(f"Extracted {len(full_text)} chars from {num_pages} pages")
        return full_text

    except Exception as e:
        logger.error(f"PDF extraction failed for {pdf_path}: {e}")
        raise ValueError(f"Could not read PDF file: {e}") from e


def parse_email_content(raw_email: str) -> dict[str, Any]:
    """
    Parse raw email text into structured fields.

    Args:
        raw_email: Raw email content with headers.

    Returns:
        Dict with parsed email fields.
    """
    result: dict[str, Any] = {
        "sender_name": "",
        "sender_email": "",
        "subject": "",
        "date": "",
        "body": "",
    }

    lines = raw_email.strip().split("\n")
    body_start = 0

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Parse From: header
        from_match = re.match(r"From:\s*(.+)", line_stripped, re.IGNORECASE)
        if from_match:
            from_value = from_match.group(1).strip()
            # Try to extract name and email
            email_match = re.search(r"<(.+?)>", from_value)
            if email_match:
                result["sender_email"] = email_match.group(1)
                result["sender_name"] = from_value[:from_value.index("<")].strip()
            else:
                result["sender_email"] = from_value
            continue

        # Parse Subject: header
        subj_match = re.match(r"Subject:\s*(.+)", line_stripped, re.IGNORECASE)
        if subj_match:
            result["subject"] = subj_match.group(1).strip()
            continue

        # Parse Date: header
        date_match = re.match(r"Date:\s*(.+)", line_stripped, re.IGNORECASE)
        if date_match:
            result["date"] = date_match.group(1).strip()
            continue

        # Parse To: header
        to_match = re.match(r"To:\s*(.+)", line_stripped, re.IGNORECASE)
        if to_match:
            continue

        # Detect body start (first empty line after headers, or first non-header line)
        if not line_stripped and i > 0:
            body_start = i + 1
            break

        # If this line doesn't look like a header, it's the start of the body
        if not re.match(r"^[A-Za-z-]+:\s", line_stripped) and i > 0:
            body_start = i
            break

    # Extract body
    if body_start > 0:
        result["body"] = "\n".join(lines[body_start:]).strip()
    else:
        result["body"] = raw_email.strip()

    return result


def validate_json_content(raw_json: str) -> tuple[bool, dict[str, Any] | None, str]:
    """
    Validate and parse JSON content.

    Args:
        raw_json: Raw JSON string.

    Returns:
        Tuple of (is_valid, parsed_data, error_message).
    """
    try:
        parsed = json.loads(raw_json.strip())
        return True, parsed, ""
    except json.JSONDecodeError as e:
        return False, None, str(e)
