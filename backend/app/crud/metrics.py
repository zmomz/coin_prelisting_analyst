import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models.metric import Metric
from app.schemas.metric import MetricCreate, MetricUpdate


async def create_metric(db: AsyncSession, metric_in: MetricCreate) -> Metric:
    metric = Metric(**metric_in.dict())
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


async def get_metric(db: AsyncSession, metric_id: uuid.UUID) -> Optional[Metric]:
    result = await db.execute(
        select(Metric).where(Metric.id == metric_id, Metric.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_metrics_by_coin(db: AsyncSession, coin_id: uuid.UUID) -> List[Metric]:
    result = await db.execute(
        select(Metric)
        .where(Metric.coin_id == coin_id, Metric.is_active == True)
    )
    return result.scalars().all()


async def update_metric(
    db: AsyncSession, db_metric: Metric, metric_in: MetricUpdate
) -> Metric:
    for field, value in metric_in.dict(exclude_unset=True).items():
        setattr(db_metric, field, value)
    await db.commit()
    await db.refresh(db_metric)
    return db_metric


async def delete_metric(db: AsyncSession, db_metric: Metric):
    db_metric.is_active = False
    await db.commit()
