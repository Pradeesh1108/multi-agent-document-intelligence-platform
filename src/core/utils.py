"""
Utility functions for the platform.
"""

def clean_llm_error(e: Exception) -> str:
    """Clean up verbose LLM API errors for the UI."""
    msg = str(e)
    if "API_KEY_INVALID" in msg or "API key not valid" in msg or "401" in msg or "authentication" in msg.lower():
        raise ValueError("Invalid API key provided. Please check your credentials.")
    # Truncate very long errors
    if len(msg) > 200:
        return msg[:197] + "..."
    return msg
