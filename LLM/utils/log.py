import os
import logging
from datetime import datetime
from functools import wraps

logger = None

def log_exceptions(func):
    """Decorator to log exceptions in a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper

def get_log_filename():
    """Generate log filename based on 2-minitue interval blocks."""
    now = datetime.now()
    # Calculate 2-minitue block start
    minitue_block_start = (now.minute // 2) * 2
    minitue_block_end = (minitue_block_start + 2) % 24
    date_label = now.strftime("%Y-%m-%d")
    filename = f"{date_label}_{minitue_block_start:02d}00-{minitue_block_end:02d}00.log"
    return os.path.join("logs_new", filename)

def setup_logger():
    """Setup logger with 2-minitue rotating log files."""
    global logger
    logger = logging.getLogger("MyAppLogger")
    logger.setLevel(logging.INFO)

    # Ensure logs directory exists
    os.makedirs("logs_new", exist_ok=True)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler for 2-minitue block log file
    file_handler = logging.FileHandler(get_log_filename())
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
