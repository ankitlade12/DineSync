"""Performance metrics tracking for DineSync.

Provides decorators and utilities for tracking API performance,
response times, and other metrics.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def track_performance(
    metadata: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]:
    """Decorator to track performance metrics of function calls.
    
    Args:
        metadata: Optional metadata to include with performance tracking
        
    Returns:
        Decorated function that tracks execution time and other metrics
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                # Log performance metrics (can be extended to send to monitoring service)
                _log_performance(
                    func.__name__,
                    elapsed,
                    metadata or {},
                    success=True
                )
                
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                _log_performance(
                    func.__name__,
                    elapsed,
                    metadata or {},
                    success=False,
                    error=str(e)
                )
                raise
        
        return cast(F, wrapper)
    
    return decorator


def _log_performance(
    function_name: str,
    elapsed_time: float,
    metadata: Dict[str, Any],
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """Log performance metrics.
    
    Args:
        function_name: Name of the function being tracked
        elapsed_time: Time taken to execute in seconds
        metadata: Additional metadata about the operation
        success: Whether the operation succeeded
        error: Error message if operation failed
    """
    # Simple console logging for now - can be extended to send to monitoring service
    status = "SUCCESS" if success else "FAILED"
    log_msg = f"[PERF] {function_name} - {status} - {elapsed_time:.3f}s"
    
    if metadata:
        log_msg += f" - {metadata}"
    
    if error:
        log_msg += f" - Error: {error}"
    
    # In production, this could send to a monitoring service like Datadog, New Relic, etc.
    # For now, we'll just print to console (visible in Streamlit logs)
    print(log_msg)
