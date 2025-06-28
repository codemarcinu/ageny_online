"""
Unit tests for database models.
Testuje modele SQLAlchemy z pełną separacją.
"""

import pytest
from datetime import datetime

from backend.models.user import User
from backend.models.conversation import Conversation, Message
from backend.models.ocr_result import OCRResult
from backend.models.cost_tracking import CostRecord


class TestUserModel:
    """Test cases for User model."""

    def test_user_creation(self):
        """Test user model creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        repr_str = repr(user)
        assert "User" in repr_str
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str

    def test_user_to_dict(self):
        """Test user to dictionary conversion."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        user_dict = user.to_dict()
        assert "username" in user_dict
        assert "email" in user_dict
        assert "hashed_password" in user_dict


class TestConversationModel:
    """Test cases for Conversation model."""

    def test_conversation_creation(self):
        """Test conversation model creation."""
        conversation = Conversation(
            title="Test Conversation",
            session_id="test-session-123",
            agent_type="general",
            provider_used="openai"
        )
        
        assert conversation.title == "Test Conversation"
        assert conversation.session_id == "test-session-123"
        assert conversation.agent_type == "general"
        assert conversation.provider_used == "openai"

    def test_conversation_repr(self):
        """Test conversation string representation."""
        conversation = Conversation(
            session_id="test-session-123",
            agent_type="general"
        )
        
        repr_str = repr(conversation)
        assert "Conversation" in repr_str
        assert "test-session-123" in repr_str
        assert "general" in repr_str


class TestMessageModel:
    """Test cases for Message model."""

    def test_message_creation(self):
        """Test message model creation."""
        message = Message(
            conversation_id=1,
            role="user",
            content="Hello, this is a test message",
            provider_used="openai",
            model_used="gpt-4",
            tokens_used=10,
            cost="0.001"
        )
        
        assert message.conversation_id == 1
        assert message.role == "user"
        assert message.content == "Hello, this is a test message"
        assert message.provider_used == "openai"
        assert message.model_used == "gpt-4"
        assert message.tokens_used == 10
        assert message.cost == "0.001"

    def test_message_repr(self):
        """Test message string representation."""
        message = Message(
            conversation_id=1,
            role="user",
            content="Test message"
        )
        
        repr_str = repr(message)
        assert "Message" in repr_str
        assert "user" in repr_str
        assert "1" in repr_str


class TestOCRResultModel:
    """Test cases for OCRResult model."""

    def test_ocr_result_creation(self):
        """Test OCR result model creation."""
        ocr_result = OCRResult(
            session_id="test-session-123",
            provider_used="mistral_vision",
            extracted_text="Extracted text from image",
            confidence=0.95,
            tokens_used=150,
            cost="0.001"
        )
        
        assert ocr_result.session_id == "test-session-123"
        assert ocr_result.provider_used == "mistral_vision"
        assert ocr_result.extracted_text == "Extracted text from image"
        assert ocr_result.confidence == 0.95
        assert ocr_result.tokens_used == 150
        assert ocr_result.cost == "0.001"

    def test_ocr_result_repr(self):
        """Test OCR result string representation."""
        ocr_result = OCRResult(
            session_id="test-session-123",
            provider_used="mistral_vision",
            extracted_text="Test text",
            confidence=0.9
        )
        
        repr_str = repr(ocr_result)
        assert "OCRResult" in repr_str
        assert "mistral_vision" in repr_str
        assert "0.9" in repr_str


class TestCostRecordModel:
    """Test cases for CostRecord model."""

    def test_cost_record_creation(self):
        """Test cost record model creation."""
        cost_record = CostRecord(
            date=datetime.now().date(),
            provider="openai",
            service_type="chat",
            cost="0.002",
            request_count=1
        )
        
        assert cost_record.provider == "openai"
        assert cost_record.service_type == "chat"
        assert cost_record.cost == "0.002"
        assert cost_record.request_count == 1

    def test_cost_record_repr(self):
        """Test cost record string representation."""
        cost_record = CostRecord(
            date=datetime.now().date(),
            provider="openai",
            service_type="chat",
            cost="0.002"
        )
        
        repr_str = repr(cost_record)
        assert "CostRecord" in repr_str
        assert "openai" in repr_str
        assert "0.002" in repr_str 