import logging
import logging.config
import sys

from app.core.config import settings

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = settings.LOG_LEVEL.upper()


def configure_logging() -> None:
    """Configure root, Uvicorn, Celery, and app-level loggers."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": LOG_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
            },
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "celery": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "app": {
                "level": LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)


# Initialize logging at import time
configure_logging()

# Main logger for app usage
logger = logging.getLogger("app")
