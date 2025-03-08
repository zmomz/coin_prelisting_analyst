import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.crud.metrics import get_metric, get_metrics_by_coin
from app.schemas.metric import MetricOut
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/{metric_id}", response_model=MetricOut)
async def get_metric_endpoint(metric_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific metric by ID."""
    metric = await get_metric(db, metric_id)
    if not metric:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    return metric


@router.get("/coin/{coin_id}", response_model=List[MetricOut])
async def get_metrics_by_coin_endpoint(
    coin_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Retrieve all metrics for a specific coin."""
    return await get_metrics_by_coin(db, coin_id)
