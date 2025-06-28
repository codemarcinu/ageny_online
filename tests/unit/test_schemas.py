"""
Unit tests for Pydantic schemas.
Testuje walidację danych z pełną separacją.
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from backend.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from backend.schemas.message import MessageCreate, MessageResponse
from backend.schemas.ocr import OCRRequest, OCRResponse, OCRBatchResponse
from backend.schemas.cost import CostRecordCreate, CostRecordResponse


class TestUserSchemas:
    """Test cases for user schemas."""

    def test_user_create_valid(self):
        """Test valid user creation schema."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "testpassword123"
        assert user.full_name == "Test User"

    def test_user_create_invalid_username(self):
        """Test invalid username validation."""
        user_data = {
            "username": "",  # Empty username
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_create_invalid_email(self):
        """Test invalid email validation."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",  # Invalid email
            "password": "testpassword123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_create_short_password(self):
        """Test short password validation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Too short
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_update_valid(self):
        """Test valid user update schema."""
        user_data = {
            "username": "newusername",
            "email": "new@example.com"
        }
        
        user = UserUpdate(**user_data)
        assert user.username == "newusername"
        assert user.email == "new@example.com"

    def test_user_response_valid(self):
        """Test valid user response schema."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user = UserResponse(**user_data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"


class TestConversationSchemas:
    """Test cases for conversation schemas."""

    def test_conversation_create_valid(self):
        """Test valid conversation creation schema."""
        conv_data = {
            "title": "Test Conversation",
            "session_id": "test-session-123",
            "agent_type": "general",
            "provider_used": "openai"
        }
        
        conv = ConversationCreate(**conv_data)
        assert conv.title == "Test Conversation"
        assert conv.session_id == "test-session-123"
        assert conv.agent_type == "general"
        assert conv.provider_used == "openai"

    def test_conversation_create_invalid_session_id(self):
        """Test invalid session ID validation."""
        conv_data = {
            "session_id": "",  # Empty session ID
            "agent_type": "general"
        }
        
        with pytest.raises(ValidationError):
            ConversationCreate(**conv_data)

    def test_conversation_create_invalid_agent_type(self):
        """Test invalid agent type validation."""
        conv_data = {
            "session_id": "test-session-123",
            "agent_type": ""  # Empty agent type
        }
        
        with pytest.raises(ValidationError):
            ConversationCreate(**conv_data)


class TestMessageSchemas:
    """Test cases for message schemas."""

    def test_message_create_valid(self):
        """Test valid message creation schema."""
        msg_data = {
            "conversation_id": 1,
            "role": "user",
            "content": "Hello, this is a test message",
            "provider_used": "openai",
            "model_used": "gpt-4",
            "tokens_used": 10,
            "cost": "0.001"
        }
        
        msg = MessageCreate(**msg_data)
        assert msg.conversation_id == 1
        assert msg.role == "user"
        assert msg.content == "Hello, this is a test message"
        assert msg.provider_used == "openai"

    def test_message_create_invalid_role(self):
        """Test invalid role validation."""
        msg_data = {
            "conversation_id": 1,
            "role": "invalid_role",  # Invalid role
            "content": "Test message"
        }
        
        with pytest.raises(ValidationError):
            MessageCreate(**msg_data)

    def test_message_create_empty_content(self):
        """Test empty content validation."""
        msg_data = {
            "conversation_id": 1,
            "role": "user",
            "content": ""  # Empty content
        }
        
        with pytest.raises(ValidationError):
            MessageCreate(**msg_data)


class TestOCRSchemas:
    """Test cases for OCR schemas."""

    def test_ocr_request_valid(self):
        """Test valid OCR request schema."""
        ocr_data = {
            "provider": "mistral_vision",
            "model": "mistral-large-latest",
            "prompt": "Extract text from this image"
        }
        
        ocr = OCRRequest(**ocr_data)
        assert ocr.provider == "mistral_vision"
        assert ocr.model == "mistral-large-latest"
        assert ocr.prompt == "Extract text from this image"

    def test_ocr_request_invalid_provider(self):
        """Test invalid provider validation."""
        ocr_data = {
            "provider": "invalid_provider"  # Invalid provider
        }
        
        with pytest.raises(ValidationError):
            OCRRequest(**ocr_data)

    def test_ocr_response_valid(self):
        """Test valid OCR response schema."""
        ocr_data = {
            "text": "Extracted text from image",
            "confidence": 0.95,
            "provider": "mistral_vision",
            "model_used": "mistral-large-latest",
            "tokens_used": 150,
            "cost": 0.001,
            "metadata": {"test": True}
        }
        
        ocr = OCRResponse(**ocr_data)
        assert ocr.text == "Extracted text from image"
        assert ocr.confidence == 0.95
        assert ocr.provider == "mistral_vision"
        assert ocr.cost == 0.001

    def test_ocr_batch_response_valid(self):
        """Test valid OCR batch response schema."""
        results = [
            {
                "text": "Text 1",
                "confidence": 0.9,
                "provider": "mistral_vision",
                "model_used": "mistral-large-latest",
                "tokens_used": 100,
                "cost": 0.001,
                "metadata": {"test": True}
            },
            {
                "text": "Text 2",
                "confidence": 0.9,
                "provider": "mistral_vision", 
                "model_used": "mistral-large-latest",
                "tokens_used": 100,
                "cost": 0.001,
                "metadata": {"test": True}
            }
        ]
        
        batch_data = {
            "results": results,
            "total_cost": 0.002,
            "total_tokens": 200
        }
        
        batch = OCRBatchResponse(**batch_data)
        assert len(batch.results) == 2
        assert batch.total_cost == 0.002
        assert batch.total_tokens == 200


class TestCostSchemas:
    """Test cases for cost schemas."""

    def test_cost_record_create_valid(self):
        """Test valid cost record creation schema."""
        cost_data = {
            "date": date.today(),
            "provider": "openai",
            "service_type": "chat",
            "cost": "0.002",
            "request_count": 1
        }
        
        cost = CostRecordCreate(**cost_data)
        assert cost.provider == "openai"
        assert cost.service_type == "chat"
        assert cost.cost == "0.002"
        assert cost.request_count == 1

    def test_cost_record_create_invalid_service_type(self):
        """Test invalid service type validation."""
        cost_data = {
            "date": date.today(),
            "provider": "openai",
            "service_type": "invalid_service",  # Invalid service type
            "cost": "0.002"
        }
        
        with pytest.raises(ValidationError):
            CostRecordCreate(**cost_data)

    def test_cost_record_create_invalid_cost(self):
        """Test invalid cost validation."""
        cost_data = {
            "date": date.today(),
            "provider": "openai",
            "service_type": "chat",
            "cost": "invalid_cost"  # Invalid cost format
        }
        
        with pytest.raises(ValidationError):
            CostRecordCreate(**cost_data) 