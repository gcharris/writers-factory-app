"""
Usage Tracking Service - Token usage and cost estimation for MVP

Tracks:
- Tokens consumed per provider
- Estimated cost in USD
- Threshold notifications when costs exceed configurable limits

This is critical for MVP course where users get free access but we need
visibility into actual costs for post-MVP pricing decisions.

Usage:
    usage_service = UsageTrackingService()

    # Record usage after an API call
    usage_service.record_usage(
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=1000,
        output_tokens=500
    )

    # Get monthly summary
    summary = usage_service.get_monthly_summary()

    # Check thresholds
    alert = usage_service.check_thresholds()
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Database Setup ---
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)
USAGE_DB_PATH = os.path.join(WORKSPACE_DIR, "sessions.db")  # Share with other services
USAGE_DB_URL = f"sqlite:///{USAGE_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(USAGE_DB_URL, echo=False)
UsageSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Pricing Data (per 1M tokens) ---
# Updated November 2025 - prices change frequently, so keep this updated
PRICING = {
    # DeepSeek - very cheap
    "deepseek": {
        "deepseek-chat": {"input": 0.14, "output": 0.28},
        "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    },
    # Qwen (Alibaba) - cheap with generous free tier
    "qwen": {
        "qwen-plus": {"input": 0.80, "output": 2.00},
        "qwen-turbo": {"input": 0.30, "output": 0.60},
        "qwen-max": {"input": 2.00, "output": 6.00},
    },
    # Mistral - European, good value
    "mistral": {
        "mistral-small": {"input": 0.10, "output": 0.30},
        "mistral-medium": {"input": 2.70, "output": 8.10},
        "mistral-large": {"input": 2.00, "output": 6.00},
    },
    # Zhipu (GLM-4) - Chinese, cheap
    "zhipu": {
        "glm-4-flash": {"input": 0.10, "output": 0.10},
        "glm-4-plus": {"input": 0.50, "output": 0.50},
    },
    # Kimi (Moonshot AI) - Chinese
    "kimi": {
        "moonshot-v1-8k": {"input": 0.50, "output": 0.50},
        "moonshot-v1-32k": {"input": 1.50, "output": 1.50},
    },
    # Yandex - Russian alternative
    "yandex": {
        "yandexgpt": {"input": 0.20, "output": 0.40},
    },
    # Anthropic - expensive, user provides keys
    "anthropic": {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    },
    # OpenAI - expensive, user provides keys
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    },
    # Google - mid-range
    "google": {
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    },
    # xAI (Grok)
    "xai": {
        "grok-2": {"input": 2.00, "output": 10.00},
        "grok-beta": {"input": 5.00, "output": 15.00},
    },
    # Ollama - free (local)
    "ollama": {
        "llama3.2:3b": {"input": 0.0, "output": 0.0},
        "llama3.2:1b": {"input": 0.0, "output": 0.0},
        "mistral:7b": {"input": 0.0, "output": 0.0},
        "deepseek-r1:7b": {"input": 0.0, "output": 0.0},
        "qwen2.5:7b": {"input": 0.0, "output": 0.0},
    },
}

# Default thresholds (USD) - can be configured
DEFAULT_THRESHOLDS = [
    {"amount": 5.0, "level": "info", "message": "You've spent about $5 this month on AI. That's normal usage!"},
    {"amount": 10.0, "level": "warning", "message": "You're approaching $10 this month. You're using AI quite a bit!"},
    {"amount": 25.0, "level": "warning", "message": "You've spent $25 this month. Consider if all these AI calls are necessary."},
    {"amount": 50.0, "level": "critical", "message": "You've exceeded $50 this month. This is higher than typical usage."},
]


# --- Database Models ---
class UsageRecord(Base):
    """Individual API usage record."""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    estimated_cost = Column(Float, nullable=False, default=0.0)
    # Context about the usage
    task_type = Column(String(50), nullable=True)  # e.g., "chat", "tournament", "health_check"
    session_id = Column(String(100), nullable=True)

    __table_args__ = (
        Index('idx_usage_month', 'timestamp'),
        Index('idx_usage_provider_month', 'provider', 'timestamp'),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost": self.estimated_cost,
            "task_type": self.task_type,
            "session_id": self.session_id,
        }


class ThresholdNotification(Base):
    """Track which thresholds have been shown to avoid spam."""
    __tablename__ = "threshold_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False, index=True)  # "2025-11"
    threshold_amount = Column(Float, nullable=False)
    notified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dismissed = Column(Integer, default=0)  # 0=active, 1=dismissed

    __table_args__ = (
        Index('idx_threshold_month', 'month', 'threshold_amount', unique=True),
    )


# Create tables
Base.metadata.create_all(bind=engine)
logger.info(f"Usage tracking tables initialized in: {USAGE_DB_PATH}")


# --- Data Classes ---
@dataclass
class UsageSummary:
    """Monthly usage summary."""
    month: str  # "2025-11"
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    record_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ThresholdAlert:
    """Alert when a cost threshold is exceeded."""
    threshold_amount: float
    current_cost: float
    level: str  # "info", "warning", "critical"
    message: str
    already_notified: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# --- Service Class ---
class UsageTrackingService:
    """
    Tracks token usage and costs across all AI providers.

    Used for:
    - MVP cost visibility (you pay, users see what they're "spending")
    - Post-MVP pricing decisions
    - Threshold notifications to prevent runaway costs
    """

    def __init__(self):
        self.pricing = PRICING
        self.thresholds = DEFAULT_THRESHOLDS

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> UsageRecord:
        """
        Record a single API usage event.

        Args:
            provider: Provider name (e.g., "deepseek", "anthropic")
            model: Model ID (e.g., "deepseek-chat", "claude-3-5-sonnet")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            task_type: Optional task type for categorization
            session_id: Optional session ID for grouping

        Returns:
            The created UsageRecord
        """
        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)

        db: Session = UsageSessionLocal()
        try:
            record = UsageRecord(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=cost,
                task_type=task_type,
                session_id=session_id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            logger.debug(
                f"Recorded usage: {provider}/{model} "
                f"{input_tokens}+{output_tokens} tokens = ${cost:.4f}"
            )
            return record

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record usage: {e}")
            raise
        finally:
            db.close()

    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost in USD for a given usage."""
        provider_pricing = self.pricing.get(provider.lower(), {})
        model_pricing = provider_pricing.get(model, None)

        if not model_pricing:
            # Try to find a partial match (model IDs can vary)
            for known_model, pricing in provider_pricing.items():
                if known_model in model or model in known_model:
                    model_pricing = pricing
                    break

        if not model_pricing:
            logger.warning(f"No pricing found for {provider}/{model}, assuming free")
            return 0.0

        # Prices are per 1M tokens
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

        return input_cost + output_cost

    def get_monthly_summary(self, month: Optional[str] = None) -> UsageSummary:
        """
        Get usage summary for a given month.

        Args:
            month: Month in "YYYY-MM" format. Defaults to current month.

        Returns:
            UsageSummary with totals and per-provider breakdown
        """
        if not month:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        # Parse month to get date range
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1, tzinfo=timezone.utc)

        # Calculate end of month
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)

        db: Session = UsageSessionLocal()
        try:
            records = db.query(UsageRecord).filter(
                UsageRecord.timestamp >= start_date,
                UsageRecord.timestamp < end_date,
            ).all()

            summary = UsageSummary(month=month)

            for record in records:
                summary.total_input_tokens += record.input_tokens
                summary.total_output_tokens += record.output_tokens
                summary.total_cost += record.estimated_cost
                summary.record_count += 1

                # Group by provider
                if record.provider not in summary.by_provider:
                    summary.by_provider[record.provider] = {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                        "models": {},
                    }

                provider_data = summary.by_provider[record.provider]
                provider_data["input_tokens"] += record.input_tokens
                provider_data["output_tokens"] += record.output_tokens
                provider_data["cost"] += record.estimated_cost

                # Track per-model within provider
                if record.model not in provider_data["models"]:
                    provider_data["models"][record.model] = {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                    }
                model_data = provider_data["models"][record.model]
                model_data["input_tokens"] += record.input_tokens
                model_data["output_tokens"] += record.output_tokens
                model_data["cost"] += record.estimated_cost

            return summary

        finally:
            db.close()

    def check_thresholds(self, month: Optional[str] = None) -> Optional[ThresholdAlert]:
        """
        Check if any cost thresholds have been exceeded.

        Returns the highest exceeded threshold that hasn't been notified yet,
        or None if no new thresholds exceeded.
        """
        summary = self.get_monthly_summary(month)
        current_cost = summary.total_cost

        if not month:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        db: Session = UsageSessionLocal()
        try:
            # Find the highest exceeded threshold that hasn't been notified
            for threshold in reversed(self.thresholds):  # Start from highest
                if current_cost >= threshold["amount"]:
                    # Check if already notified
                    existing = db.query(ThresholdNotification).filter(
                        ThresholdNotification.month == month,
                        ThresholdNotification.threshold_amount == threshold["amount"],
                    ).first()

                    alert = ThresholdAlert(
                        threshold_amount=threshold["amount"],
                        current_cost=current_cost,
                        level=threshold["level"],
                        message=threshold["message"],
                        already_notified=existing is not None,
                    )

                    # Mark as notified if not already
                    if not existing:
                        notification = ThresholdNotification(
                            month=month,
                            threshold_amount=threshold["amount"],
                        )
                        db.add(notification)
                        db.commit()

                    return alert

            return None

        finally:
            db.close()

    def dismiss_threshold(self, month: str, threshold_amount: float) -> bool:
        """Mark a threshold notification as dismissed."""
        db: Session = UsageSessionLocal()
        try:
            notification = db.query(ThresholdNotification).filter(
                ThresholdNotification.month == month,
                ThresholdNotification.threshold_amount == threshold_amount,
            ).first()

            if notification:
                notification.dismissed = 1
                db.commit()
                return True
            return False

        finally:
            db.close()

    def get_recent_usage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent usage records for debugging/display."""
        db: Session = UsageSessionLocal()
        try:
            records = db.query(UsageRecord).order_by(
                UsageRecord.timestamp.desc()
            ).limit(limit).all()

            return [r.to_dict() for r in records]

        finally:
            db.close()

    def get_daily_breakdown(self, month: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get daily cost breakdown for charts."""
        if not month:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1, tzinfo=timezone.utc)

        if month_num == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)

        db: Session = UsageSessionLocal()
        try:
            records = db.query(UsageRecord).filter(
                UsageRecord.timestamp >= start_date,
                UsageRecord.timestamp < end_date,
            ).all()

            # Group by day
            daily: Dict[str, float] = {}
            for record in records:
                day = record.timestamp.strftime("%Y-%m-%d")
                daily[day] = daily.get(day, 0) + record.estimated_cost

            # Convert to list sorted by date
            return [
                {"date": date, "cost": cost}
                for date, cost in sorted(daily.items())
            ]

        finally:
            db.close()

    def reset_month(self, month: str) -> int:
        """
        Reset usage data for a month (admin function).

        Returns number of records deleted.
        """
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1, tzinfo=timezone.utc)

        if month_num == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)

        db: Session = UsageSessionLocal()
        try:
            deleted = db.query(UsageRecord).filter(
                UsageRecord.timestamp >= start_date,
                UsageRecord.timestamp < end_date,
            ).delete()

            # Also reset threshold notifications
            db.query(ThresholdNotification).filter(
                ThresholdNotification.month == month,
            ).delete()

            db.commit()
            logger.info(f"Reset {deleted} usage records for {month}")
            return deleted

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to reset month: {e}")
            raise
        finally:
            db.close()


# Singleton instance
usage_tracking_service = UsageTrackingService()
