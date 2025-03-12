import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from app.tasks.scoring import recalculate_scores
from app.crud.metrics import create_metric
from app.schemas.metric import MetricCreate


@pytest.mark.asyncio(loop_scope="session")
@patch("app.services.scoring.update_coin_score", new_callable=AsyncMock)
async def test_recalculate_scores(
    mock_update_score,
    db_session: AsyncSession,
    test_coin
):
    """Test that scoring task correctly updates coin scores."""
    # Create test metrics for the coin
    await create_metric(
        db_session,
        MetricCreate(
            coin_id=test_coin.id,
            market_cap={
                "usd": 1000000,
                "normalized": 0.8
            },
            volume_24h={
                "usd": 50000,
                "normalized": 0.6
            }
        )
    )

    # Mocking as it doesn't return anything
    mock_update_score.return_value = None

    await recalculate_scores()

    # Verify the mock was called
    mock_update_score.assert_called()
