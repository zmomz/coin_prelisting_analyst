from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.models.metric import Metric
from app.schemas.metric import MetricResponseSchema, MetricValueSchema, MetricCreate
from sqlalchemy import delete


async def create_metric(db: AsyncSession, metric_data: MetricCreate) -> MetricResponseSchema:
    """Create a new metric entry in the database."""
    metric_dict = metric_data.model_dump()  # ✅ Convert Pydantic model to dictionary

    db_metric = Metric(**metric_dict)
    db.add(db_metric)
    await db.commit()
    await db.refresh(db_metric)

    return db_metric


async def get_metric_by_id(db: AsyncSession, metric_id: UUID):
    """Retrieve a single metric by its ID."""
    result = await db.execute(select(Metric).where(Metric.id == metric_id))
    metric = result.scalar_one_or_none()

    if metric is None:
        return None

    return MetricResponseSchema(
        id=metric.id,
        coin_id=metric.coin_id,
        market_cap=MetricValueSchema(**metric.market_cap),  # ✅ Now correctly parsed
        volume_24h=MetricValueSchema(**metric.volume_24h),
        liquidity=MetricValueSchema(**metric.liquidity),
        github_activity=metric.github_activity,
        twitter_sentiment=metric.twitter_sentiment,
        reddit_sentiment=metric.reddit_sentiment,
        fetched_at=metric.fetched_at,
        is_active=metric.is_active,
        created_at=metric.created_at,
    )


async def get_metrics_by_coin(db: AsyncSession, coin_id: UUID):
    """Retrieve all metrics for a given coin."""
    result = await db.execute(select(Metric).where(Metric.coin_id == coin_id))
    metrics = result.scalars().all()

    return [
        MetricResponseSchema(
            id=metric.id,
            coin_id=metric.coin_id,
            market_cap=MetricValueSchema(**metric.market_cap),
            volume_24h=MetricValueSchema(**metric.volume_24h),
            liquidity=MetricValueSchema(**metric.liquidity),
            github_activity=metric.github_activity,
            twitter_sentiment=metric.twitter_sentiment,
            reddit_sentiment=metric.reddit_sentiment,
            fetched_at=metric.fetched_at,
            is_active=metric.is_active,
            created_at=metric.created_at,
        )
        for metric in metrics
    ]


async def delete_metric(db: AsyncSession, metric_id: UUID) -> bool:
    """Delete a metric by its ID."""
    result = await db.execute(delete(Metric).where(Metric.id == metric_id))
    await db.commit()

    return result.rowcount > 0  # Returns True if deletion was successful