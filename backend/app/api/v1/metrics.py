from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.schemas.metric import MetricResponseSchema
from app.crud.metrics import get_metric_by_id, get_metrics_by_coin

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/{metric_id}", response_model=MetricResponseSchema)
async def get_metric(metric_id: UUID, db: AsyncSession = Depends(get_db)):
    """API to get a metric by its ID."""
    metric = await get_metric_by_id(db, metric_id)

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    return metric


@router.get("/coin/{coin_id}", response_model=list[MetricResponseSchema])
async def get_metrics_by_coin_api(coin_id: UUID, db: AsyncSession = Depends(get_db)):
    """API to get all metrics for a given coin."""
    metrics = await get_metrics_by_coin(db, coin_id)

    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this coin")

    return metrics
