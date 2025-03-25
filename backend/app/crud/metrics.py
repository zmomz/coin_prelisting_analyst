from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app.models.metric import Metric
from app.schemas.metric import MetricCreate, MetricUpdate


async def create_metric(db: AsyncSession, metric_in: MetricCreate) -> Metric:
    """Create a new metric entry in the database."""
    metric = Metric(**metric_in.model_dump())
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


async def get_metric_by_id(db: AsyncSession, metric_id: UUID) -> Metric | None:
    """Retrieve a single metric by its ID."""
    result = await db.execute(select(Metric).where(Metric.id == metric_id, Metric.is_active == True))
    return result.scalar_one_or_none()


async def get_metrics_by_coin(db: AsyncSession, coin_id: UUID) -> list[Metric]:
    """Retrieve all metrics for a given coin."""
    result = await db.execute(select(Metric).where(Metric.coin_id == coin_id, Metric.is_active == True))
    return result.scalars().all()


async def update_metric(
    db: AsyncSession, db_metric: Metric, metric_in: MetricUpdate
) -> Metric:
    """Update a metric in the database."""
    for field, value in metric_in.model_dump(exclude_unset=True).items():
        setattr(db_metric, field, value)
    await db.commit()
    await db.refresh(db_metric)
    return db_metric


async def delete_metric(db: AsyncSession, db_metric: Metric) -> None:
    """Soft delete a metric."""
    db_metric.is_active = False
    await db.commit()


def create_metric_sync(db: Session, metric_in: MetricCreate) -> Metric:
    metric = Metric(**metric_in.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric