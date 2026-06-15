"""
Tests for the LLM Factory pattern.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.core.config import LLMProvider
from src.core.llm_factory import LLMFactory


class TestLLMFactory:
    """Test suite for LLMFactory provider creation."""

    @patch("src.core.llm_factory.get_settings")
    def test_create_defaults_to_settings_provider(self, mock_settings):
        """Factory should use settings.LLM_PROVIDER when no provider arg given."""
        settings = MagicMock()
        settings.LLM_PROVIDER = LLMProvider.GEMINI
        settings.GOOGLE_API_KEY = "test-key"
        settings.GEMINI_MODEL = "gemini-2.0-flash"
        mock_settings.return_value = settings

        with patch("src.core.llm_factory.LLMFactory._create_gemini") as mock_gemini:
            mock_gemini.return_value = MagicMock()
            LLMFactory.create()
            mock_gemini.assert_called_once()

    @patch("src.core.llm_factory.get_settings")
    def test_create_with_explicit_gemini(self, mock_settings):
        """Factory should create Gemini when explicitly requested."""
        settings = MagicMock()
        settings.GOOGLE_API_KEY = "test-key"
        settings.GEMINI_MODEL = "gemini-2.0-flash"
        mock_settings.return_value = settings

        with patch("src.core.llm_factory.LLMFactory._create_gemini") as mock_gemini:
            mock_gemini.return_value = MagicMock()
            LLMFactory.create(provider="gemini")
            mock_gemini.assert_called_once()

    @patch("src.core.llm_factory.get_settings")
    def test_create_with_explicit_groq(self, mock_settings):
        """Factory should create Groq when explicitly requested."""
        settings = MagicMock()
        settings.GROQ_API_KEY = "test-key"
        settings.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.return_value = settings

        with patch("src.core.llm_factory.LLMFactory._create_groq") as mock_groq:
            mock_groq.return_value = MagicMock()
            LLMFactory.create(provider="groq")
            mock_groq.assert_called_once()

    def test_create_with_unknown_provider_raises(self):
        """Factory should raise ValueError for unknown providers."""
        with pytest.raises(ValueError):
            LLMFactory.create(provider="openai")

    @patch("src.core.llm_factory.get_settings")
    def test_gemini_without_api_key_raises(self, mock_settings):
        """Gemini creation should fail without GOOGLE_API_KEY."""
        settings = MagicMock()
        settings.GOOGLE_API_KEY = ""
        settings.GEMINI_MODEL = "gemini-2.0-flash"
        mock_settings.return_value = settings

        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            LLMFactory._create_gemini(0.3, 4096)

    @patch("src.core.llm_factory.get_settings")
    def test_groq_without_api_key_raises(self, mock_settings):
        """Groq creation should fail without GROQ_API_KEY."""
        settings = MagicMock()
        settings.GROQ_API_KEY = ""
        settings.GROQ_MODEL = "llama-3.3-70b-versatile"
        mock_settings.return_value = settings

        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            LLMFactory._create_groq(0.3, 4096)

    @patch("src.core.llm_factory.get_settings")
    def test_custom_temperature(self, mock_settings):
        """Factory should pass temperature to provider creation."""
        settings = MagicMock()
        settings.LLM_PROVIDER = LLMProvider.GEMINI
        settings.GOOGLE_API_KEY = "test-key"
        settings.GEMINI_MODEL = "gemini-2.0-flash"
        mock_settings.return_value = settings

        with patch("src.core.llm_factory.LLMFactory._create_gemini") as mock_gemini:
            mock_gemini.return_value = MagicMock()
            LLMFactory.create(temperature=0.0)
            mock_gemini.assert_called_once_with(0.0, 4096)
