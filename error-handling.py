from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import traceback
import threading
from queue import Queue
import logging

@dataclass
class SystemError:
    """Represents a system error."""
    error_id: str
    error_type: str
    component: str
    message: str
    stack_trace: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    severity: str = "ERROR"
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0

class ErrorHandler:
    """Handles system errors and manages recovery."""
    
    def __init__(self, event_monitor=None):
        self.error_queue = Queue()
        self.error_history = []
        self.recovery_strategies = {}
        self.error_callbacks = {}
        self.is_running = True
        self.event_monitor = event_monitor
        self.logger = logging.getLogger(__name__)
        
        # Start error processing thread
        self.processing_thread = threading.Thread(target=self._process_errors)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Registers a recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy

    def register_error_callback(self, error_type: str, callback: Callable):
        """Registers a callback for an error type."""
        self.error_callbacks[error_type] = callback

    def handle_error(self, error: Exception, component: str, context: Dict[str, Any] = None):
        """Handles a system error."""
        error_id = f"ERR_{datetime.now().timestamp()}"
        
        system_error = SystemError(
            error_id=error_id,
            error_type=type(error).__name__,
            component=component,
            message=str(error),
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
        
        self.error_queue.put(system_error)
        
        # Log error event if monitor exists
        if self.event_monitor:
            self.event_monitor.log_event(
                SystemEvent(
                    event_type="ERROR",
                    component=component,
                    message=str(error),
                    severity="ERROR",
                    metadata={
                        'error_id': error_id,
                        'error_type': type(error).__name__,
                        'context': context
                    }
                )
            )
        
        return error_id

    def _process_errors(self):
        """Processes errors from the queue."""
        while self.is_running:
            try:
                error = self.error_queue.get(timeout=1.0)
                self._handle_single_error(error)
            except Queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in error processing: {str(e)}")

    def _handle_single_error(self, error: SystemError):
        """Handles a single system error."""
        try:
            # Store in history
            self.error_history.append(error)
            
            # Try recovery strategy
            if error.error_type in self.recovery_strategies:
                try:
                    strategy = self.recovery_strategies[error.error_type]
                    strategy(error)
                    self._log_recovery_success(error)
                except Exception as e:
                    self._log_recovery_failure(error, e)
                    
            # Execute callback if registered
            if error.error_type in self.error_callbacks:
                try:
                    callback = self.error_callbacks[error.error_type]
                    callback(error)
                except Exception as e:
                    self.logger.error(f"Error in error callback: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error handling error: {str(e)}")

    def _log_recovery_success(self, error: SystemError):
        """Logs successful error recovery."""
        if self.event_monitor:
            self.event_monitor.log_event(
                SystemEvent(
                    event_type="RECOVERY_SUCCESS",
                    component=error.component,
                    message=f"Successfully recovered from {error.error_type}",
                    severity="INFO",
                    metadata={
                        'error_id': error.error_id,
                        'recovery_attempts': error.recovery_attempts
                    }
                )
            )

    def _log_recovery_failure(self, error: SystemError, recovery_error: Exception):
        """Logs failed error recovery."""
        if self.event_monitor:
            self.event_monitor.log_event(
                SystemEvent(
                    event_type="RECOVERY_FAILURE",
                    component=error.component,
                    message=f"Failed to recover from {error.error_type}: {str(recovery_error)}",
                    severity="ERROR",
                    metadata={
                        'error_id': error.error_id,
                        'recovery_attempts': error.recovery_attempts,
                        'recovery_error': str(recovery_error)
                    }
                )
            )

    def get_error_history(
        self,
        component: Optional[str] = None,
        error_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[SystemError]:
        """Retrieves filtered error history."""
        filtered_errors = self.error_history

        if component:
            filtered_errors = [
                e for e in filtered_errors
                if e.component == component
            ]

        if error_type:
            filtered_errors = [
                e for e in filtered_errors
                if e.error_type == error_type
            ]

        if start_time:
            filtered_errors = [
                e for e in filtered_errors
                if e.timestamp >= start_time
            ]

        if end_time:
            filtered_errors = [
                e for e in filtered_errors
                if e.timestamp <= end_time
            ]

        return filtered_errors

    def get_error_summary(self) -> Dict[str, Any]:
        """Generates summary of system errors."""
        summary = {
            'total_errors': len(self.error_history),
            'errors_by_type': {},
            'errors_by_component': {},
            'recovery_success_rate': 0.0
        }

        recovery_attempts = 0
        recovery_successes = 0

        for error in self.error_history:
            # Count by type
            if error.error_type not in summary['errors_by_type']:
                summary['errors_by_type'][error.error_type] = 0
            summary['errors_by_type'][error.error_type] += 1

            # Count by component
            if error.component not in summary['errors_by_component']:
                summary['errors_by_component'][error.component] = 0
            summary['errors_by_component'][error.component] += 1

            # Track recovery statistics
            if error.recovery_attempts > 0:
                recovery_attempts += 1
                if error.error_type in self.recovery_strategies:
                    recovery_successes += 1

        if recovery_attempts > 0:
            summary['recovery_success_rate'] = recovery_successes / recovery_attempts

        return summary

class ErrorRecoveryManager:
    """Manages system recovery strategies."""
    
    def __init__(self, handler: ErrorHandler):
        self.handler = handler
        self.recovery_attempts = {}
        self.max_attempts = 3
        self.recovery_intervals = [5, 15, 30]  # seconds
        
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Registers default recovery strategies."""
        self.handler.register_recovery_strategy(
            "ConnectionError",
            self._handle_connection_error
        )
        self.handler.register_recovery_strategy(
            "MemoryError",
            self._handle_memory_error
        )
        self.handler.register_recovery_strategy(
            "TimeoutError",
            self._handle_timeout_error
        )

    def _handle_connection_error(self, error: SystemError):
        """Handles connection-related errors."""
        attempt = self.recovery_attempts.get(error.error_id, 0)
        
        if attempt < self.max_attempts:
            # Implement connection retry logic
            self.recovery_attempts[error.error_id] = attempt + 1
            error.recovery_attempts += 1
            
            # Sleep for increasing intervals between attempts
            time.sleep(self.recovery_intervals[attempt])
            
            # Attempt reconnection
            try:
                # Implement reconnection logic
                pass
            except Exception as e:
                raise RecoveryError(f"Failed to recover connection: {str(e)}")

    def _handle_memory_error(self, error: SystemError):
        """Handles memory-related errors."""
        # Implement memory cleanup and optimization
        try:
            # Garbage collection
            import gc
            gc.collect()
            
            # Clear caches
            # Implement cache clearing logic
            
            error.recovery_attempts += 1
        except Exception as e:
            raise RecoveryError(f"Failed to recover from memory error: {str(e)}")

    def _handle_timeout_error(self, error: SystemError):
        """Handles timeout-related errors."""
        attempt = self.recovery_attempts.get(error.error_id, 0)
        
        if attempt < self.max_attempts:
            # Implement retry logic with increased timeout
            self.recovery_attempts[error.error_id] = attempt + 1
            error.recovery_attempts += 1
            
            try:
                # Implement retry logic
                pass
            except Exception as e:
                raise RecoveryError(f"Failed to recover from timeout: {str(e)}")

class RecoveryError(Exception):
    """Custom exception for recovery failures."""
    pass

class SystemStateValidator:
    """Validates system state during recovery."""
    
    def __init__(self):
        self.validators = {}
        self._register_default_validators()

    def _register_default_validators(self):
        """Registers default state validators."""
        self.validators.update({
            'memory': self._validate_memory_state,
            'connections': self._validate_connections,
            'processes': self._validate_processes
        })

    def validate_state(self, component: str) -> bool:
        """Validates system state for a component."""
        validators = self.validators.get(component, [])
        
        for validator in validators:
            if not validator():
                return False
        return True

    def _validate_memory_state(self) -> bool:
        """Validates memory state."""
        try:
            import psutil
            memory = psutil.Process().memory_percent()
            return memory < 90.0  # Example threshold
        except:
            return True  # Default to true if can't check

    def _validate_connections(self) -> bool:
        """Validates system connections."""
        # Implement connection validation logic
        return True

    def _validate_processes(self) -> bool:
        """Validates system processes."""
        # Implement process validation logic
        return True
