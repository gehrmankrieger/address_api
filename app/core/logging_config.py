import logging.config

LOG_FORMAT = "%(asctime)s | %(levelname)-4s | %(name)s | %(message)s"

def setup_logging(level: str = "INFO") -> None:
    """One time configuration, so all formats are the same."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": LOG_FORMAT},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": level.upper(), 
                "handlers": ["console"]
            },
            "loggers": {
                "uvicorn": {
                    "handlers": [], 
                    "propagate": True,
                    "level": "INFO"
                },
            },
        }
    )