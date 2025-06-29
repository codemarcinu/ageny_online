"""
Integration tests for Tutor Antonina endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.fixture
def client():
    """Create test client."""
    from src.backend.api.main import app
    return TestClient(app)


@pytest.fixture
def mock_llm_factory():
    """Mock LLM factory for testing."""
    with patch('src.backend.api.v2.endpoints.chat.llm_factory') as mock:
        # Mock provider
        mock_provider = AsyncMock()
        mock_provider.chat.return_value = {
            "choices": [{"message": {"content": "Test AI response"}}],
            "model": "gpt-4",
            "provider": "openai",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "cost": 0.001,
            "finish_reason": "stop"
        }
        
        # Mock provider factory methods
        mock.get_available_providers.return_value = [type('ProviderType', (), {'value': 'openai'})()]
        mock.get_provider.return_value = mock_provider
        mock.chat_with_fallback.return_value = {
            "choices": [{"message": {"content": "Test AI response"}}],
            "model": "gpt-4",
            "provider": "openai",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "cost": 0.001,
            "finish_reason": "stop"
        }
        
        yield mock


@pytest.fixture
def mock_tutor_agent():
    """Mock Tutor Antonina agent."""
    with patch('src.backend.api.v2.endpoints.chat.TutorAntonina') as mock:
        mock_instance = AsyncMock()
        mock_instance.guide.return_value = {
            "question": "W jakim kontekście chcesz użyć tego prompta?",
            "feedback": None
        }
        mock.return_value = mock_instance
        yield mock


class TestTutorEndpoints:
    """Test cases for Tutor Antonina endpoints."""
    
    def test_chat_with_tutor_mode(self, client, mock_llm_factory, mock_tutor_agent):
        """Test chat endpoint with tutor mode enabled."""
        response = client.post("/api/v2/chat/chat", json={
            "messages": [
                {"role": "user", "content": "Napisz esej"}
            ],
            "tutor_mode": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "tutor_question" in data
        assert "tutor_feedback" in data
        assert data["tutor_question"] == "W jakim kontekście chcesz użyć tego prompta?"
        assert data["tutor_feedback"] is None
    
    def test_chat_without_tutor_mode(self, client, mock_llm_factory):
        """Test chat endpoint without tutor mode."""
        response = client.post("/api/v2/chat/chat", json={
            "messages": [
                {"role": "user", "content": "Napisz esej"}
            ],
            "tutor_mode": False
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert data["tutor_question"] is None
        assert data["tutor_feedback"] is None
    
    def test_tutor_endpoint(self, client, mock_llm_factory, mock_tutor_agent):
        """Test dedicated tutor endpoint."""
        response = client.post("/api/v2/chat/tutor", json={
            "messages": [
                {"role": "user", "content": "Napisz esej"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reply" in data
        assert "tutor_question" in data
        assert "tutor_feedback" in data
        assert "model" in data
        assert "provider" in data
        assert "usage" in data
        assert "cost" in data
        assert "finish_reason" in data
        assert "response_time" in data
    
    def test_tutor_endpoint_with_feedback(self, client, mock_llm_factory, mock_tutor_agent):
        """Test tutor endpoint when prompt is complete."""
        # Mock tutor agent to return feedback instead of question
        mock_tutor_agent.return_value.guide.return_value = {
            "question": None,
            "feedback": "Sugestia: Twój prompt jest dobry.\n\nUlepszony prompt: [ulepszona wersja]"
        }
        
        response = client.post("/api/v2/chat/tutor", json={
            "messages": [
                {"role": "user", "content": "Kompletny prompt"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tutor_question"] is None
        assert "Sugestia: Twój prompt jest dobry" in data["tutor_feedback"]
    
    def test_tutor_endpoint_error_handling(self, client, mock_llm_factory, mock_tutor_agent):
        """Test tutor endpoint error handling."""
        # Mock tutor agent to raise exception
        mock_tutor_agent.return_value.guide.side_effect = Exception("Test error")
        
        response = client.post("/api/v2/chat/tutor", json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ]
        })
        
        assert response.status_code == 500
        assert "Tutor mode failed" in response.json()["detail"]
    
    def test_chat_with_tutor_mode_error_handling(self, client, mock_llm_factory, mock_tutor_agent):
        """Test chat endpoint with tutor mode error handling."""
        # Mock tutor agent to raise exception
        mock_tutor_agent.return_value.guide.side_effect = Exception("Test error")
        
        response = client.post("/api/v2/chat/chat", json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ],
            "tutor_mode": True
        })
        
        # Should not fail the entire request
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "Przepraszam, wystąpił błąd w trybie tutora" in data["tutor_question"]
        assert data["tutor_feedback"] is None
    
    def test_invalid_request(self, client):
        """Test invalid request handling."""
        response = client.post("/api/v2/chat/tutor", json={
            "messages": []  # Empty messages
        })
        
        assert response.status_code == 400
        assert "At least one message is required" in response.json()["detail"]
    
    def test_tutor_endpoint_with_provider(self, client, mock_llm_factory, mock_tutor_agent):
        """Test tutor endpoint with specific provider."""
        response = client.post("/api/v2/chat/tutor", json={
            "messages": [
                {"role": "user", "content": "Test prompt"}
            ],
            "provider": "openai",
            "model": "gpt-4"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4" 