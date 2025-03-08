import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from app.tasks.scoring import recalculate_scores
from app.services.scoring import update_coin_score


@pytest.mark.asyncio
@patch("app.services.scoring.update_coin_score", new_callable=AsyncMock)
async def test_recalculate_scores(mock_update_score, db_session: AsyncSession):
    """Test that scoring task correctly updates coin scores."""
    mock_update_score.return_value = None  # Mocking as it doesn't return anything

    await recalculate_scores()

    # Verify the mock was called
    mock_update_score.assert_called()
