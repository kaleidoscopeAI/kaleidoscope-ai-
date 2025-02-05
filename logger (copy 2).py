import logging
import os

# Configure the logger
LOG_FILE = os.path.join("logs", "kaleidoscope_ai.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Helper functions for logging
def log_info(message: str):
    """
    Logs an informational message.
    """
    logging.info(message)

def log_warning(message: str):
    """
    Logs a warning message.
    """
    logging.warning(message)

def log_error(message: str):
    """
    Logs an error message.
    """
    logging.error(message)

def log_debug(message: str):
    """
    Logs a debug message.
    """
    logging.debug(message)

# Example usage
if __name__ == "__main__":
    log_info("Kaleidoscope AI system initialized.")
    log_warning("System running low on energy resources.")
    log_error("Node replication failed due to insufficient energy.")
    log_debug("Debugging node cluster allocation.")
