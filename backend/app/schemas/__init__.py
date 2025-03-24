from pydantic import BaseModel
from pydantic.config import ConfigDict


class SchemaBase(BaseModel):
    """Base class for all schemas with shared config."""

    model_config = ConfigDict(from_attributes=True)
