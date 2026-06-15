"""
LLM Factory — Central factory for creating LLM instances.

Supports dynamic provider swapping via environment variables.
All agents obtain LLM instances through this factory, never directly.

Usage:
    from src.core.llm_factory import LLMFactory

    llm = LLMFactory.create()                    # Uses default provider from settings
    llm = LLMFactory.create(provider="groq")     # Override provider
    llm = LLMFactory.create(temperature=0.0)     # Custom temperature
"""

from langchain_core.language_models import BaseChatModel

from src.core.config import LLMProvider, get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMFactory:
    """
    Factory for creating LLM instances based on provider configuration.

    Supports:
        - Google Gemini (via langchain-google-genai)
        - Groq (via langchain-groq)

    The active provider is determined by:
        1. Explicit `provider` argument
        2. LLM_PROVIDER environment variable
    """

    @staticmethod
    def create(
        provider: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> BaseChatModel:
        """
        Create an LLM instance for the specified provider.

        Args:
            provider: LLM provider name ("gemini" or "groq").
                      Defaults to settings.LLM_PROVIDER.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
            max_tokens: Maximum output tokens.

        Returns:
            A configured LangChain chat model instance.

        Raises:
            ValueError: If the provider is unknown or API key is missing.
        """
        settings = get_settings()
        resolved_provider = LLMProvider(provider) if provider else settings.LLM_PROVIDER

        if resolved_provider == LLMProvider.GEMINI:
            return LLMFactory._create_gemini(temperature, max_tokens, api_key)
        elif resolved_provider == LLMProvider.GROQ:
            return LLMFactory._create_groq(temperature, max_tokens, api_key)
        else:
            raise ValueError(
                f"Unknown LLM provider: '{resolved_provider}'. "
                f"Supported: {[p.value for p in LLMProvider]}"
            )

    @staticmethod
    def _create_gemini(temperature: float, max_tokens: int, api_key: str | None) -> BaseChatModel:
        """Create a Google Gemini chat model instance."""
        from langchain_google_genai import ChatGoogleGenerativeAI

        settings = get_settings()
        key_to_use = api_key or settings.GOOGLE_API_KEY
        if not key_to_use:
            raise ValueError(
                "GOOGLE_API_KEY is required for the Gemini provider. "
                "Set it in your .env file or provide it via the UI."
            )

        logger.info(f"Creating Gemini LLM instance: model={settings.GEMINI_MODEL}")
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=key_to_use,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

    @staticmethod
    def _create_groq(temperature: float, max_tokens: int, api_key: str | None) -> BaseChatModel:
        """Create a Groq chat model instance."""
        from langchain_groq import ChatGroq

        settings = get_settings()
        key_to_use = api_key or settings.GROQ_API_KEY
        if not key_to_use:
            raise ValueError(
                "GROQ_API_KEY is required for the Groq provider. "
                "Set it in your .env file or provide it via the UI."
            )

        logger.info(f"Creating Groq LLM instance: model={settings.GROQ_MODEL}")
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=key_to_use,
            temperature=temperature,
            max_tokens=max_tokens,
        )
