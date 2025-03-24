from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_manager
from app.models.user import User
from app.schemas.metric import MetricCreate, MetricUpdate, MetricOut
from app.crud.metrics import (
    create_metric,
    get_metric_by_id,
    get_metrics_by_coin,
    update_metric,
    delete_metric,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/", response_model=MetricOut, status_code=status.HTTP_201_CREATED)
async def create_metric_endpoint(
    metric_in: MetricCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> MetricOut:
    """Create a new metric (manager only)."""
    metric = await create_metric(db, metric_in)
    return metric


@router.get("/{metric_id}", response_model=MetricOut, status_code=status.HTTP_200_OK)
async def get_metric_endpoint(
    metric_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MetricOut:
    """Retrieve a single metric by ID."""
    metric = await get_metric_by_id(db, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.get("/coin/{coin_id}", response_model=list[MetricOut], status_code=status.HTTP_200_OK)
async def get_metrics_by_coin_endpoint(
    coin_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MetricOut]:
    """List all metrics for a given coin."""
    return await get_metrics_by_coin(db, coin_id)


@router.put("/{metric_id}", response_model=MetricOut, status_code=status.HTTP_200_OK)
async def update_metric_endpoint(
    metric_id: UUID,
    metric_in: MetricUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> MetricOut:
    """Update a metric (manager only)."""
    db_metric = await get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    return await update_metric(db, db_metric, metric_in)


@router.delete("/{metric_id}", status_code=status.HTTP_200_OK)
async def delete_metric_endpoint(
    metric_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> dict:
    """Soft delete a metric (manager only)."""
    db_metric = await get_metric_by_id(db, metric_id)
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    await delete_metric(db, db_metric)
    return {"detail": "Metric deleted successfully"}
