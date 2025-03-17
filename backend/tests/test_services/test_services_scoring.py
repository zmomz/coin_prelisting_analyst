import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.score import Score
from app.services.scoring import recalculate_scores_service


@pytest.mark.asyncio(loop_scope="session")
async def test_recalculate_scores_no_coins(db_session: AsyncSession):
    """
    If there are no active coins in the DB, the service should return:
    {"success": False, "error": "No active coins found"}.
    
    We do NOT call `test_coin` here, so no coins get created.
    """
    result = await recalculate_scores_service(db_session)
    assert result["success"] is False
    assert "No active coins found" in result["error"]


@pytest.mark.asyncio(loop_scope="session")
async def test_recalculate_scores_no_weights(db_session: AsyncSession, test_coin):
    """
    If there is at least one active coin but NO scoring weight, 
    the service should return:
    {"success": False, "error": "No scoring weights found"}.
    
    Here `test_coin` fixture creates an active coin automatically.
    We do NOT call `scoring_weight`, so no weight is created.
    """
    # test_coin fixture created an active coin.
    result = await recalculate_scores_service(db_session)
    assert result["success"] is False
    assert "No scoring weights found" in result["error"]


@pytest.mark.asyncio(loop_scope="session")
async def test_recalculate_scores_happy_path(db_session: AsyncSession, test_coin, test_metrics, scoring_weight):
    """
    If we have at least one active coin, at least one metric, 
    and a scoring weight, the service should create Score entries 
    and return success.
    
    - test_coin fixture -> creates a single active coin
    - test_metrics fixture -> creates multiple metrics for that coin
    - scoring_weight fixture -> creates one valid ScoringWeight
    """
    result = await recalculate_scores_service(db_session)

    # The service picks the "latest metric" per coin (by fetched_at).
    # Even if `test_metrics` adds multiple, only the newest is used
    # for the final score. So we expect 1 score to be created.
    assert result["success"] is True
    assert result["updated_scores"] == 1

    # Confirm a new Score row was inserted for the coin created by `test_coin`.
    # `test_coin` returns a coin, so we can filter by coin.id:
    coin_id = test_coin.id
    scores_stmt = select(Score).where(Score.coin_id == coin_id)
    row = (await db_session.execute(scores_stmt)).scalars().all()

    assert len(row) == 1, "Exactly one Score entry should exist"
    new_score = row[0]

    # Optionally check final_score range or other fields:
    assert 0 <= new_score.final_score <= 1, "Final score must be in [0, 1]"
    assert new_score.final_score > 0, "Expected a positive final score"
    print("Final Score:", new_score.final_score)
