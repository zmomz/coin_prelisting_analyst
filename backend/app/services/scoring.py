import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.coin import Coin
from app.models.metric import Metric
from app.models.scoring_weight import ScoringWeight
from app.models.score import Score
from app.schemas.score import ScoreIn

logger = logging.getLogger(__name__)


async def recalculate_scores_service(db: AsyncSession):
    """
    Recalculate scores for all active coins, using the latest metrics (subquery).
    """
    try:
        # Step 1) Gather active coins
        coin_ids_result = await db.execute(
            select(Coin.id).where(Coin.is_active)
        )
        coin_ids = [row[0] for row in coin_ids_result.fetchall()]

        if not coin_ids:
            return {"success": False, "error": "No active coins found"}

        # Step 2) Fetch the latest scoring weight
        weight_query = select(ScoringWeight).order_by(ScoringWeight.created_at.desc())
        scoring_weight = (await db.execute(weight_query)).scalar_one_or_none()
        if not scoring_weight:
            return {"success": False, "error": "No scoring weights found"}

        # Step 3) subquery to get (coin_id, max(fetched_at)) per coin
        latest_metrics_subq = (
            select(
                Metric.coin_id.label("coin_id"),
                func.max(Metric.fetched_at).label("max_fetched_at")
            )
            .where(Metric.coin_id.in_(coin_ids))
            .group_by(Metric.coin_id)
            .subquery()
        )

        # Step 4) join subquery back to Metric table
        metrics_stmt = (
            select(Metric)
            .join(
                latest_metrics_subq,
                (Metric.coin_id == latest_metrics_subq.c.coin_id)
                & (Metric.fetched_at == latest_metrics_subq.c.max_fetched_at)
            )
        )
        metrics_list = (await db.execute(metrics_stmt)).scalars().all()

        # Group metrics by coin_id
        metrics_by_coin_id = {m.coin_id: m for m in metrics_list}

        # Retrieve all active coins
        coin_stmt = select(Coin).where(Coin.id.in_(coin_ids))
        coin_objects = (await db.execute(coin_stmt)).scalars().all()

        scores_updated = 0

        for coin in coin_objects:
            metrics = metrics_by_coin_id.get(coin.id)
            if not metrics:
                # No metric => skip
                continue

            # Safeguard: get each numeric value
            liquidity_val = metrics.liquidity.get("value", 0) or 0
            volume_val = metrics.volume_24h.get("value", 0) or 0
            github_val = metrics.github_activity.get("count", 0) or 0
            twitter_val = metrics.twitter_sentiment.get("score", 0) or 0
            reddit_val = metrics.reddit_sentiment.get("score", 0) or 0
            market_cap_val = metrics.market_cap.get("value", 0) or 0

            # Convert raw metrics => partial scores
            liquidity_score = min(1.0, (liquidity_val + volume_val) / 1_000_000)
            developer_score = min(1.0, github_val / 500)
            community_score = min(1.0, (twitter_val + reddit_val) / 2)
            market_score = min(1.0, market_cap_val / 10_000_000)

            # Weighted final
            final_score = (
                (liquidity_score * scoring_weight.liquidity_score)
                + (developer_score * scoring_weight.developer_score)
                + (community_score * scoring_weight.community_score)
                + (market_score * scoring_weight.market_score)
            )
            final_score = max(0.0, min(final_score, 1.0))

            # Insert into Score
            score_in = ScoreIn(
                coin_id=coin.id,
                scoring_weight_id=scoring_weight.id,
                liquidity_score=liquidity_score,
                developer_score=developer_score,
                community_score=community_score,
                market_score=market_score,
                final_score=final_score,
            )
            new_score = Score(**score_in.model_dump())
            db.add(new_score)
            scores_updated += 1

        await db.commit()

        if scores_updated == 0:
            msg = "No scores were updated (no valid metrics found)"
            logger.info(msg)
            return {"success": False, "error": msg}

    except Exception as e:
        await db.rollback()
        logger.error(f"Error recalculating scores: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

    logger.info(f"Scores updated: {scores_updated}")
    return {"success": True, "updated_scores": scores_updated}
