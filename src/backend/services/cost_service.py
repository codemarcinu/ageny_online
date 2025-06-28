"""
Cost tracking service for Ageny Online.
Zapewnia logikę biznesową śledzenia kosztów z pełną separacją.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.models.cost_tracking import CostRecord
from backend.schemas.cost import CostRecordCreate
from backend.exceptions.database import ValidationError

logger = logging.getLogger(__name__)


class CostService:
    """Service for cost tracking operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def record_cost(self, cost_data: CostRecordCreate) -> CostRecord:
        """Record a cost entry.

        Args:
            cost_data: Cost record creation data

        Returns:
            Created cost record instance

        Raises:
            ValidationError: If cost recording fails
        """
        try:
            cost_record = CostRecord(
                user_id=cost_data.user_id,
                date=cost_data.date,
                provider=cost_data.provider,
                service_type=cost_data.service_type,
                model_used=cost_data.model_used,
                tokens_used=cost_data.tokens_used,
                cost=cost_data.cost,
                request_count=cost_data.request_count,
                metadata=cost_data.metadata
            )

            self.db_session.add(cost_record)
            await self.db_session.commit()
            await self.db_session.refresh(cost_record)

            logger.info(
                f"Cost recorded: provider={cost_data.provider}, "
                f"service={cost_data.service_type}, cost={cost_data.cost}"
            )
            return cost_record

        except Exception as e:
            logger.error(f"Failed to record cost: {e}")
            await self.db_session.rollback()
            raise ValidationError(f"Failed to record cost: {e}")

    async def get_cost_records(
        self, 
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider: Optional[str] = None,
        service_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostRecord]:
        """Get cost records with filters.

        Args:
            user_id: Filter by user ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            provider: Filter by provider (optional)
            service_type: Filter by service type (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of cost record instances
        """
        query = select(CostRecord)
        
        if user_id:
            query = query.where(CostRecord.user_id == user_id)
        if start_date:
            query = query.where(CostRecord.date >= start_date)
        if end_date:
            query = query.where(CostRecord.date <= end_date)
        if provider:
            query = query.where(CostRecord.provider == provider)
        if service_type:
            query = query.where(CostRecord.service_type == service_type)
        
        result = await self.db_session.execute(
            query.order_by(CostRecord.date.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_cost_summary(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get cost summary statistics.

        Args:
            user_id: Filter by user ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)

        Returns:
            Dictionary with cost summary
        """
        query = select(CostRecord)
        
        if user_id:
            query = query.where(CostRecord.user_id == user_id)
        if start_date:
            query = query.where(CostRecord.date >= start_date)
        if end_date:
            query = query.where(CostRecord.date <= end_date)
        
        result = await self.db_session.execute(query)
        records = result.scalars().all()
        
        if not records:
            return {
                "total_cost": 0.0,
                "total_requests": 0,
                "total_tokens": 0,
                "providers": {},
                "services": {}
            }
        
        total_cost = sum(float(r.cost) for r in records)
        total_requests = sum(r.request_count for r in records)
        total_tokens = sum(r.tokens_used or 0 for r in records)
        
        # Group by provider
        providers = {}
        for record in records:
            provider = record.provider
            if provider not in providers:
                providers[provider] = {
                    "cost": 0.0,
                    "requests": 0,
                    "tokens": 0
                }
            providers[provider]["cost"] += float(record.cost)
            providers[provider]["requests"] += record.request_count
            providers[provider]["tokens"] += record.tokens_used or 0
        
        # Group by service type
        services = {}
        for record in records:
            service = record.service_type
            if service not in services:
                services[service] = {
                    "cost": 0.0,
                    "requests": 0,
                    "tokens": 0
                }
            services[service]["cost"] += float(record.cost)
            services[service]["requests"] += record.request_count
            services[service]["tokens"] += record.tokens_used or 0
        
        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "providers": providers,
            "services": services
        }

    async def get_daily_costs(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get daily cost breakdown.

        Args:
            user_id: Filter by user ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)

        Returns:
            List of daily cost summaries
        """
        query = select(
            CostRecord.date,
            func.sum(func.cast(CostRecord.cost, func.Float)).label("total_cost"),
            func.sum(CostRecord.request_count).label("total_requests"),
            func.sum(CostRecord.tokens_used).label("total_tokens")
        ).group_by(CostRecord.date)
        
        if user_id:
            query = query.where(CostRecord.user_id == user_id)
        if start_date:
            query = query.where(CostRecord.date >= start_date)
        if end_date:
            query = query.where(CostRecord.date <= end_date)
        
        result = await self.db_session.execute(
            query.order_by(CostRecord.date.desc())
        )
        
        return [
            {
                "date": row.date.isoformat(),
                "total_cost": float(row.total_cost or 0),
                "total_requests": row.total_requests or 0,
                "total_tokens": row.total_tokens or 0
            }
            for row in result
        ]

    async def check_budget_alert(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Check if costs exceed budget thresholds.

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            Dictionary with budget alert information
        """
        from backend.config import settings
        
        # Get current month costs
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        summary = await self.get_cost_summary(
            user_id=user_id,
            start_date=start_of_month,
            end_date=today
        )
        
        total_cost = summary["total_cost"]
        monthly_budget = settings.MONTHLY_BUDGET
        alert_threshold = settings.COST_ALERT_THRESHOLD
        
        budget_percentage = (total_cost / monthly_budget) * 100 if monthly_budget > 0 else 0
        
        return {
            "total_cost": total_cost,
            "monthly_budget": monthly_budget,
            "budget_percentage": budget_percentage,
            "alert_threshold": alert_threshold,
            "alert_triggered": budget_percentage >= alert_threshold,
            "over_budget": total_cost > monthly_budget
        } 