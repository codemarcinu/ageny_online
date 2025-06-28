"""
User service for Ageny Online.
Zapewnia logikę biznesową użytkowników z pełną separacją.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate
from backend.exceptions.database import ValidationError

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            ValidationError: If user creation fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValidationError(f"User with email {user_data.email} already exists")

            # Hash password
            hashed_password = pwd_context.hash(user_data.password)

            # Create user
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=user_data.is_active
            )

            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)

            logger.info(f"User created successfully: {user.username}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to create user: {e}")

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None
        """
        result = await self.db_session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None
        """
        result = await self.db_session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user data.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user instance or None

        Raises:
            ValidationError: If update fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            # Update fields
            for field, value in user_data.dict(exclude_unset=True).items():
                setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(user)

            logger.info(f"User updated successfully: {user.username}")
            return user

        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to update user: {e}")

    async def delete_user(self, user_id: int) -> bool:
        """Delete user.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion fails
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            await self.db_session.delete(user)
            await self.db_session.commit()

            logger.info(f"User deleted successfully: {user.username}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to delete user: {e}")

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user instances
        """
        result = await self.db_session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password) 