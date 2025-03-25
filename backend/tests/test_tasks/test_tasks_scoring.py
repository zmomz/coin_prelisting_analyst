# import uuid
# from datetime import datetime

# import pytest
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.coin import Coin
# from app.models.metric import Metric
# from app.models.score import Score
# from app.models.scoring_weight import ScoringWeight
# from app.services.scoring import recalculate_scores_service
# from app.tasks.scoring import recalculate_scores_async


# @pytest.mark.asyncio(loop_scope="session")
# async def test_no_coins(db_session: AsyncSession):
#     """
#     If there are no active coins, recalc should return:
#       {"success": False, "error": "No active coins found"}
#     """
#     result = await recalculate_scores_service(db_session)
#     assert result["success"] is False
#     assert "No active coins found" in result["error"]


# @pytest.mark.asyncio(loop_scope="session")
# async def test_no_weights(db_session: AsyncSession):
#     """
#     If we have an active coin but no scoring weight,
#     we get "No scoring weights found".
#     """
#     coin = Coin(
#         id=uuid.uuid4(),
#         coingeckoid="fakecoingecko",
#         name="Fake Coin",
#         symbol="FAKE",
#         description="Just a test coin",
#         github="https://github.com/fake",
#         is_active=True,
#     )
#     db_session.add(coin)
#     await db_session.commit()

#     result = await recalculate_scores_service(db_session)
#     assert result["success"] is False
#     assert "No scoring weights found" in result["error"]


# @pytest.mark.asyncio(loop_scope="session")
# async def test_happy_path(db_session: AsyncSession):
#     """
#     If we have at least one active coin, a valid scoring weight,
#     and a valid metric, we should successfully create Score rows.
#     """
#     # 1) Create an active coin
#     coin_id = uuid.uuid4()
#     coin = Coin(
#         id=coin_id,
#         coingeckoid="happycoingecko",
#         name="Happy Coin",
#         symbol="HAPPY",
#         description="Test coin for scoring",
#         github="https://github.com/happycoin",
#         is_active=True,
#     )
#     db_session.add(coin)

#     # 2) Create a metric for that coin
#     metric = Metric(
#         id=uuid.uuid4(),
#         coin_id=coin_id,
#         market_cap={"value": 2_000_000, "currency": "USD"},
#         volume_24h={"value": 90_000, "currency": "USD"},
#         liquidity={"value": 10_000, "currency": "USD"},
#         github_activity={"count": 50},
#         twitter_sentiment={"score": 0.6},
#         reddit_sentiment={"score": 0.7},
#         fetched_at=datetime.now(),
#         is_active=True,
#     )
#     db_session.add(metric)

#     # 3) Create a scoring weight
#     weight = ScoringWeight(
#         id=uuid.uuid4(),
#         liquidity_score=0.3,
#         developer_score=0.2,
#         community_score=0.2,
#         market_score=0.3,
#     )
#     db_session.add(weight)
#     await db_session.commit()

#     # 4) Call the service
#     result = await recalculate_scores_service(db_session)
#     assert result["success"] is True
#     assert result["updated_scores"] == 1

#     # 5) Confirm a Score row was created
#     score_rows = (
#         (await db_session.execute(select(Score).where(Score.coin_id == coin_id)))
#         .scalars()
#         .all()
#     )
#     assert len(score_rows) == 1
#     new_score = score_rows[0]
#     assert 0 <= new_score.final_score <= 1


# @pytest.mark.asyncio(loop_scope="session")
# async def test_celery_wrapper(db_session: AsyncSession):
#     """
#     Test the celery wrapper `recalculate_scores_async` to ensure it
#     calls the same logic.
#     """
#     # If no coins, same result
#     result = await recalculate_scores_async()
#     # Our code returns None, but logs "No active coins" internally.
#     # The real logic is in recalculate_scores_service
#     # So we can't do much here except ensure it doesn't crash.
#     # If you want, you can patch recalc service or check logs.
#     assert result is None
