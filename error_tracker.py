system_monitoring/logging/error_tracker.py
Python

import traceback
from datetime import datetime

class ErrorTracker:
    def __init__(self, system_logger: SystemLogger):
        self.system_logger = system_logger
        self.error_log = []

    def track_error(self, error: Exception, context_info: dict = None):
        """Track an error with relevant context information."""
        timestamp = datetime.now()
        error_message = str(error)
        stack_trace = traceback.format_exc()

        error_record = {
            'timestamp': timestamp,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'context': context_info
        }
        self.error_log.append(error_record)

        # Log the error using the SystemLogger
        logger = self.system_logger.get_logger("error_tracker")
        logger.error(f"Error: {error_message}\nContext: {context_info}\nStack Trace:\n{stack_trace}")

    def get_recent_errors(self, n: int = 10) -> list:
        """Get the n most recent error records."""
        return self.error_log[-n:]

    def clear_errors(self):
        """Clear the error log."""
        self.error_log = []
        
    def get_state(self) -> dict:
        """Returns the current state of the error tracker."""
        return {
            'error_count': len(self.error_log),
            'last_error': self.error_log[-1] if self.error_log else None
        }

