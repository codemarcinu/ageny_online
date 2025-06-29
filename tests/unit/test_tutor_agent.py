"""
Unit tests for Tutor Antonina agent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.agents.tutor_agent import TutorAntonina


@pytest.fixture
def mock_llm_factory():
    """Mock LLM factory for testing."""
    with patch('backend.agents.tutor_agent.llm_factory') as mock:
        # Mock provider
        mock_provider = AsyncMock()
        mock_provider.chat.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        
        # Mock provider factory methods
        mock.get_available_providers.return_value = [MagicMock(value="openai")]
        mock.get_provider.return_value = mock_provider
        mock.get_default_provider.return_value = mock_provider
        
        yield mock


@pytest.fixture
def tutor_agent():
    """Create Tutor Antonina agent instance."""
    return TutorAntonina(model="gpt-4", provider="openai")


class TestTutorAntonina:
    """Test cases for Tutor Antonina agent."""
    
    def test_init(self, tutor_agent):
        """Test agent initialization."""
        assert tutor_agent.config.agent_type == "tutor_antonina"
        assert tutor_agent.config.name == "Tutor Antonina"
        assert tutor_agent.model == "gpt-4"
        assert tutor_agent.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_guide_with_question(self, tutor_agent, mock_llm_factory):
        """Test guide method when prompt needs clarification."""
        # Mock response that asks a question
        mock_llm_factory.get_provider.return_value.chat.return_value = {
            "choices": [{"message": {"content": "W jakim kontekście chcesz użyć tego prompta?"}}]
        }
        
        result = await tutor_agent.guide("Napisz esej", [])
        
        assert result["question"] == "W jakim kontekście chcesz użyć tego prompta?"
        assert result["feedback"] is None
    
    @pytest.mark.asyncio
    async def test_guide_with_feedback(self, tutor_agent, mock_llm_factory):
        """Test guide method when prompt is complete."""
        # Mock response with suggestion
        mock_llm_factory.get_provider.return_value.chat.return_value = {
            "choices": [{"message": {"content": "Sugestia: Twój prompt jest dobry.\n\nUlepszony prompt: [ulepszona wersja]"}}]
        }
        
        result = await tutor_agent.guide("Kompletny prompt", [])
        
        assert result["question"] is None
        assert "Twój prompt jest dobry" in result["feedback"]
        assert "Ulepszony prompt:" in result["feedback"]
    
    @pytest.mark.asyncio
    async def test_guide_with_chat_history(self, tutor_agent, mock_llm_factory):
        """Test guide method with chat history context."""
        chat_history = [
            {"role": "user", "content": "Pierwsza wiadomość"},
            {"role": "assistant", "content": "Odpowiedź"}
        ]
        
        await tutor_agent.guide("Nowy prompt", chat_history)
        
        # Verify that chat history was included in the request
        call_args = mock_llm_factory.get_provider.return_value.chat.call_args
        messages = call_args[1]["messages"]
        
        assert len(messages) == 2
        assert "Kontekst z poprzednich wiadomości" in messages[1]["content"]
    
    @pytest.mark.asyncio
    async def test_guide_error_handling(self, tutor_agent, mock_llm_factory):
        """Test guide method error handling."""
        mock_llm_factory.get_provider.return_value.chat.side_effect = Exception("Test error")
        
        result = await tutor_agent.guide("Test prompt", [])
        
        assert result["question"] == "Przepraszam, wystąpił błąd. Spróbuj ponownie sformułować swój prompt."
        assert result["feedback"] is None
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, tutor_agent, mock_llm_factory):
        """Test process_query method success case."""
        mock_llm_factory.get_provider.return_value.chat.return_value = {
            "choices": [{"message": {"content": "Test question"}}]
        }
        
        result = await tutor_agent.process_query("Test prompt")
        
        assert result.success is True
        assert "🤔 **Pytanie od Tutora Antoniny:**" in result.content
        assert result.agent_type == "tutor_antonina"
    
    @pytest.mark.asyncio
    async def test_process_query_error(self, tutor_agent, mock_llm_factory):
        """Test process_query method error handling."""
        mock_llm_factory.get_provider.return_value.chat.side_effect = Exception("Test error")
        
        result = await tutor_agent.process_query("Test prompt")
        
        # When guide fails, it returns a question with error message, so success should be True
        assert result.success is True
        assert "Przepraszam, wystąpił błąd podczas analizy prompta" in result.content
        assert tutor_agent.error_count == 1
    
    def test_get_current_time(self, tutor_agent):
        """Test _get_current_time method."""
        time1 = tutor_agent._get_current_time()
        time2 = tutor_agent._get_current_time()
        
        assert isinstance(time1, float)
        assert isinstance(time2, float)
        assert time2 >= time1 