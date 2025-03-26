from sqlalchemy import func
from sqlalchemy.orm import Session
from app.crud.metrics import get_latest_active_by_coin_sync
from app.models import Metric, ScoringWeight, Score
from app.schemas.score import ScoreCreate
from uuid import UUID
from loguru import logger


def find_max_metrics(db: Session) -> dict:
    """Find the maximum values for each metric across all coins."""
    logger.debug("[Scoring] Fetching max metrics for normalization...")
    max_metrics = db.query(
        func.max(Metric.liquidity).label('max_liquidity'),
        func.max(Metric.github_activity).label('max_github_activity'),
        func.max(func.coalesce(Metric.twitter_sentiment, 0) +
                 func.coalesce(Metric.reddit_sentiment, 0)).label('max_community'),
        func.max(func.coalesce(Metric.market_cap, 0) +
                 func.coalesce(Metric.volume_24h, 0)).label('max_market')
    ).first()

    results = {
        'max_liquidity': max_metrics.max_liquidity or 1,
        'max_github_activity': max_metrics.max_github_activity or 1,
        'max_community': max_metrics.max_community or 1,
        'max_market': max_metrics.max_market or 1
    }

    logger.debug("[Scoring] Max metrics: {}", results)
    return results


def calculate_component_scores(metric: Metric, max_metrics: dict) -> dict:
    """Calculate normalized scores for each component."""
    scores = {
        "liquidity_score": min(1, (metric.liquidity or 0) / max_metrics['max_liquidity']),
        "developer_score": min(1, (metric.github_activity or 0) / max_metrics['max_github_activity']),
        "community_score": min(1, ((metric.twitter_sentiment or 0) + (metric.reddit_sentiment or 0)) / max_metrics['max_community']),
        "market_score": min(1, ((metric.market_cap or 0) + (metric.volume_24h or 0)) / max_metrics['max_market']),
    }
    logger.debug("[Scoring] Normalized component scores: {}", scores)
    return scores


def calculate_final_score(components: dict, weights: ScoringWeight) -> float:
    final = round(
        (components["liquidity_score"] * weights.liquidity_score) +
        (components["developer_score"] * weights.developer_score) +
        (components["community_score"] * weights.community_score) +
        (components["market_score"] * weights.market_score),
        4
    )
    logger.debug("[Scoring] Final weighted score: {}", final)
    return final


def upsert_score(db: Session, score_in: ScoreCreate) -> Score:
    logger.debug("[Scoring] Upserting score for coin_id={} weight_id={}", score_in.coin_id, score_in.scoring_weight_id)
    existing = (
        db.query(Score)
        .filter(
            Score.coin_id == score_in.coin_id,
            Score.scoring_weight_id == score_in.scoring_weight_id,
        )
        .first()
    )

    if existing:
        logger.info("[Scoring] Updating existing score entry.")
        existing.liquidity_score = score_in.liquidity_score
        existing.developer_score = score_in.developer_score
        existing.community_score = score_in.community_score
        existing.market_score = score_in.market_score
        existing.final_score = score_in.final_score
        db.add(existing)
    else:
        logger.info("[Scoring] Creating new score entry.")
        new_score = Score(**score_in.model_dump())
        db.add(new_score)

    db.commit()
    return existing if existing else new_score


def score_coin(
    db: Session,
    coin_id: UUID,
    scoring_weight: ScoringWeight
) -> None:
    logger.info("[Scoring] Starting score computation for coin_id={}...", coin_id)

    metric = get_latest_active_by_coin_sync(db, coin_id)
    if not metric:
        logger.warning("[Scoring] No active metric found for coin_id={}", coin_id)
        return

    max_metrics = find_max_metrics(db)
    components = calculate_component_scores(metric, max_metrics)
    final_score = calculate_final_score(components, scoring_weight)

    score_data = ScoreCreate(
        coin_id=coin_id,
        scoring_weight_id=scoring_weight.id,
        liquidity_score=components["liquidity_score"],
        developer_score=components["developer_score"],
        community_score=components["community_score"],
        market_score=components["market_score"],
        final_score=min(1, final_score),  # Ensure final score is within [0, 1]
    )

    upsert_score(db, score_data)
    logger.success("[Scoring] Scoring complete for coin_id={}", coin_id)
