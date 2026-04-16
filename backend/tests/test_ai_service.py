import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.ai_service import AIService


def test_ai_service_builds_openai_llm():
    service = AIService.__new__(AIService)
    with patch("backend.services.ai_service.ChatOpenAI") as MockOpenAI:
        llm = service._build_llm(
            provider="openai",
            api_key="sk-test",
            base_url=None,
            model="gpt-4o-mini",
        )
        MockOpenAI.assert_called_once()

def test_ai_service_builds_deepseek_llm():
    service = AIService.__new__(AIService)
    with patch("backend.services.ai_service.ChatOpenAI") as MockOpenAI:
        llm = service._build_llm(
            provider="deepseek",
            api_key="ds-test",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )
        call_kwargs = MockOpenAI.call_args[1]
        assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"
