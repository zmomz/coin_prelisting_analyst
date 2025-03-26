# app/scripts/seed_scoring_weights.py
import sys
import os
import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import ScoringWeight
from loguru import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def seed_weight(
    db: Session,
    liquidity: float,
    developer: float,
    community: float,
    market: float,
):
    weight_data = {
        "liquidity_score": liquidity,
        "developer_score": developer,
        "community_score": community,
        "market_score": market,
    }

    total = sum(weight_data.values())
    if round(total, 4) != 1.0:
        logger.error("Weights must sum to 1.0. Current sum: {}", total)
        return

    exists = db.query(ScoringWeight).filter_by(**weight_data).first()
    if exists:
        logger.info("ScoringWeight already exists: {}", weight_data)
        return

    weight = ScoringWeight(**weight_data)
    db.add(weight)
    db.commit()
    logger.success("✅ ScoringWeight inserted: {}", weight_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed a custom ScoringWeight")

    parser.add_argument("--liquidity", type=float, required=True, help="Liquidity weight")
    parser.add_argument("--developer", type=float, required=True, help="Developer activity weight")
    parser.add_argument("--community", type=float, required=True, help="Community sentiment weight")
    parser.add_argument("--market", type=float, required=True, help="Market data weight")

    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_weight(
            db=db,
            liquidity=args.liquidity,
            developer=args.developer,
            community=args.community,
            market=args.market,
        )
    finally:
        db.close()
        logger.info("Database session closed.")
