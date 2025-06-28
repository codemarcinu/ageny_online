"""
Conversation service for Ageny Online.
Zapewnia logikę biznesową konwersacji z pełną separacją.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.conversation import Conversation, Message
from backend.schemas.conversation import ConversationCreate, ConversationUpdate
from backend.schemas.message import MessageCreate
from backend.exceptions.database import ValidationError

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation management operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation.

        Args:
            conversation_data: Conversation creation data

        Returns:
            Created conversation instance

        Raises:
            ValidationError: If conversation creation fails
        """
        try:
            conversation = Conversation(
                title=conversation_data.title,
                session_id=conversation_data.session_id,
                user_id=conversation_data.user_id,
                agent_type=conversation_data.agent_type,
                provider_used=conversation_data.provider_used,
                metadata=conversation_data.metadata
            )

            self.db_session.add(conversation)
            await self.db_session.commit()
            await self.db_session.refresh(conversation)

            logger.info(f"Conversation created successfully: {conversation.session_id}")
            return conversation

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to create conversation: {e}")

    async def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation instance or None
        """
        result = await self.db_session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID.

        Args:
            session_id: Session ID

        Returns:
            Conversation instance or None
        """
        result = await self.db_session.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_conversation(self, conversation_id: int, conversation_data: ConversationUpdate) -> Optional[Conversation]:
        """Update conversation data.

        Args:
            conversation_id: Conversation ID
            conversation_data: Conversation update data

        Returns:
            Updated conversation instance or None

        Raises:
            ValidationError: If update fails
        """
        try:
            conversation = await self.get_conversation_by_id(conversation_id)
            if not conversation:
                return None

            # Update fields
            for field, value in conversation_data.dict(exclude_unset=True).items():
                setattr(conversation, field, value)

            conversation.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(conversation)

            logger.info(f"Conversation updated successfully: {conversation.session_id}")
            return conversation

        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to update conversation: {e}")

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion fails
        """
        try:
            conversation = await self.get_conversation_by_id(conversation_id)
            if not conversation:
                return False

            await self.db_session.delete(conversation)
            await self.db_session.commit()

            logger.info(f"Conversation deleted successfully: {conversation.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to delete conversation: {e}")

    async def list_conversations(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """List conversations with pagination.

        Args:
            user_id: Filter by user ID (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of conversation instances
        """
        query = select(Conversation)
        if user_id:
            query = query.where(Conversation.user_id == user_id)
        
        result = await self.db_session.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def add_message(self, conversation_id: int, message_data: MessageCreate) -> Message:
        """Add message to conversation.

        Args:
            conversation_id: Conversation ID
            message_data: Message creation data

        Returns:
            Created message instance

        Raises:
            ValidationError: If message creation fails
        """
        try:
            message = Message(
                conversation_id=conversation_id,
                role=message_data.role,
                content=message_data.content,
                provider_used=message_data.provider_used,
                model_used=message_data.model_used,
                tokens_used=message_data.tokens_used,
                cost=message_data.cost,
                processing_time=message_data.processing_time,
                metadata=message_data.metadata
            )

            self.db_session.add(message)
            await self.db_session.commit()
            await self.db_session.refresh(message)

            logger.info(f"Message added successfully to conversation {conversation_id}")
            return message

        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to add message: {e}")

    async def get_messages(self, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages for conversation.

        Args:
            conversation_id: Conversation ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of message instances
        """
        result = await self.db_session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all() 