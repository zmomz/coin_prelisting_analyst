"""Import all models here."""

from app.models.coin import Coin
from app.models.user import User
from app.models.metric import Metric
from app.models.scoring_weight import ScoringWeight
from app.models.score import Score
from app.models.suggestion import Suggestion

__all__ = ["Coin", "User", "Metric", "ScoringWeight", "Score", "Suggestion"]
