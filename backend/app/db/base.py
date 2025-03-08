from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models via the models package to avoid circular dependencies
import app.models  # This ensures all models are registered
