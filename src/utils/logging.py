import os
import glob
import logging
from src.helpers import LOGS_DATA


def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    Instantiates logger to write to specific log file
    ---
    Args:
        name (str): name of logger
        log_file (str): target filename or relative path for log file
        level (int): logging level
    Returns:
        logging.Logger: configured logger instance
    """

    if not os.path.isabs(log_file):
        if not log_file.endswith(".log"):
            log_file += ".log"
        log_file = os.path.join(LOGS_DATA, log_file)
    # ensures directory for the log file exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # creates named logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    return logger


def clear_logs(log_dir=LOGS_DATA) -> None:
    """
    Clears contents of all .log files in the log directory
    ---
    Args:
        log_dir (str): the path to the directory containing the .log files
    """
    # ensures the log directories exists
    os.makedirs(log_dir, exist_ok=True)
    # uses .glob to find all of the files in the directory
    log_files = glob.glob(str(log_dir / "*.log"))
    for log_path in log_files:
        # overwrites the logs with zero length (clearing the logs)
        with open(log_path, "w") as f:
            f.truncate(0)
        print(f"Cleared: {log_path}")
    return None
