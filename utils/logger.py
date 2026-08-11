import logging
from pathlib import Path


def get_logger(name: str = "medical_knowledge_agent") -> logging.Logger:
    """Return the application's file and console logger without duplicate handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    Path("logs").mkdir(exist_ok=True)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = logging.FileHandler("logs/agent.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
