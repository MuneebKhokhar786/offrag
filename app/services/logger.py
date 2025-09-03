import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Configure root logger for the project."""
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    formatter = logging.Formatter(log_format)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Rotating file handler (keeps logs manageable)
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5_000_000,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Silence overly noisy loggers (optional)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger
