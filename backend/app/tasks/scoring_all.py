# app/tasks/scoring.py
from app.celery_app import celery_app
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.scoringsync import score_coin
from app.crud.scoring_weights import getsync
from app.crud.coins import get_all_sync
from uuid import UUID

from loguru import logger


@celery_app.task(name="app.tasks.scoring_all.score_all_coins")
def score_all_coins(scoring_weight_id: str = "f890475c-ad0e-4b52-8cc2-ba3d02e5cacf") -> str:
    logger.info(f"[Scoring Task] Starting bulk scoring with weight_id={scoring_weight_id}")
    db: Session = SessionLocal()
    try:
        weight = getsync(db, UUID(scoring_weight_id))
        if not weight:
            logger.warning(f"[Scoring Task] ScoringWeight {scoring_weight_id} not found")
            return f"ScoringWeight {scoring_weight_id} not found"

        coins = get_all_sync(db)
        logger.info(f"[Scoring Task] Found {len(coins)} coins to score")

        for coin in coins:
            logger.debug(f"[Scoring Task] Scoring coin_id={coin.id}")
            score_coin(db, coin.id, weight)

        logger.success(f"[Scoring Task] Successfully scored {len(coins)} coins with weight_id={scoring_weight_id}")
        return f"Scored {len(coins)} coins using ScoringWeight {scoring_weight_id}"

    except Exception as e:
        db.rollback()
        logger.exception(f"[Scoring Task] Failed scoring with weight_id={scoring_weight_id}: {e}")
        raise e
    finally:
        db.close()
        logger.info(f"[Scoring Task] Database session closed for weight_id={scoring_weight_id}")