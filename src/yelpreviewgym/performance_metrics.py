"""Performance Metrics Tracking for YelpReviewGym

Tracks API response times, function execution times, and provides
performance statistics for monitoring and optimization.
"""

from __future__ import annotations

import time
import functools
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    
    function_name: str
    start_time: float
    end_time: float
    duration_ms: float
    timestamp: str
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceTracker:
    """Track and analyze performance metrics."""
    
    def __init__(self, save_path: str = "performance_metrics.json"):
        self.save_path = Path(save_path)
        self.metrics: List[PerformanceMetric] = []
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from file."""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Keep only recent metrics (last 1000)
                    recent = data.get("metrics", [])[-1000:]
                    self.metrics = [
                        PerformanceMetric(**m) for m in recent
                    ]
            except (json.JSONDecodeError, IOError, TypeError):
                self.metrics = []
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            data = {
                "metrics": [
                    {
                        "function_name": m.function_name,
                        "start_time": m.start_time,
                        "end_time": m.end_time,
                        "duration_ms": m.duration_ms,
                        "timestamp": m.timestamp,
                        "success": m.success,
                        "error": m.error,
                        "metadata": m.metadata
                    }
                    for m in self.metrics[-1000:]  # Keep last 1000
                ]
            }
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except (IOError, TypeError):
            pass
    
    def record(self, metric: PerformanceMetric):
        """Record a performance metric."""
        self.metrics.append(metric)
        self._save_metrics()
    
    def get_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        if function_name:
            filtered = [m for m in self.metrics if m.function_name == function_name]
        else:
            filtered = self.metrics
        
        if not filtered:
            return {
                "count": 0,
                "avg_duration_ms": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
                "success_rate": 0
            }
        
        durations = [m.duration_ms for m in filtered]
        successes = sum(1 for m in filtered if m.success)
        
        return {
            "count": len(filtered),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "success_rate": (successes / len(filtered)) * 100
        }
    
    def get_recent_metrics(self, limit: int = 10) -> List[PerformanceMetric]:
        """Get most recent metrics."""
        return self.metrics[-limit:]
    
    def clear_metrics(self):
        """Clear all metrics."""
        self.metrics = []
        self._save_metrics()


# Global tracker instance
_tracker = PerformanceTracker()


def get_tracker() -> PerformanceTracker:
    """Get the global performance tracker."""
    return _tracker


def track_performance(function: Optional[Callable] = None, *, metadata: Optional[Dict[str, Any]] = None):
    """Decorator to track function performance.
    
    Usage:
        @track_performance
        def my_function():
            pass
        
        @track_performance(metadata={"api": "yelp"})
        def api_call():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = True
            error = None
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                metric = PerformanceMetric(
                    function_name=func.__name__,
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    timestamp=datetime.now().isoformat(),
                    success=success,
                    error=error,
                    metadata=metadata or {}
                )
                
                _tracker.record(metric)
        
        return wrapper
    
    if function is None:
        # Called with arguments: @track_performance(metadata={...})
        return decorator
    else:
        # Called without arguments: @track_performance
        return decorator(function)


def format_performance_report(tracker: Optional[PerformanceTracker] = None) -> str:
    """Format a performance report as a string."""
    if tracker is None:
        tracker = _tracker
    
    # Get unique function names
    function_names = list(set(m.function_name for m in tracker.metrics))
    
    report = """
╔══════════════════════════════════════════════════════════╗
║         YELP REVIEW GYM - PERFORMANCE REPORT             ║
╚══════════════════════════════════════════════════════════╝

"""
    
    # Overall stats
    overall = tracker.get_stats()
    report += f"""📊 OVERALL STATISTICS
─────────────────────────────────────────────────────────────
Total Operations:    {overall['count']:,}
Success Rate:        {overall['success_rate']:.1f}%
Avg Duration:        {overall['avg_duration_ms']:.2f}ms
Min Duration:        {overall['min_duration_ms']:.2f}ms
Max Duration:        {overall['max_duration_ms']:.2f}ms

"""
    
    # Per-function stats
    if function_names:
        report += """📈 PER-FUNCTION STATISTICS
─────────────────────────────────────────────────────────────
"""
        for func_name in sorted(function_names):
            stats = tracker.get_stats(func_name)
            report += f"""
Function: {func_name}
  Calls:        {stats['count']:,}
  Success:      {stats['success_rate']:.1f}%
  Avg Time:     {stats['avg_duration_ms']:.2f}ms
  Range:        {stats['min_duration_ms']:.2f}ms - {stats['max_duration_ms']:.2f}ms
"""
    
    # Recent activity
    recent = tracker.get_recent_metrics(5)
    if recent:
        report += """
🕐 RECENT ACTIVITY (Last 5 operations)
─────────────────────────────────────────────────────────────
"""
        for i, metric in enumerate(reversed(recent), 1):
            status = "✅" if metric.success else "❌"
            report += f"{i}. {status} {metric.function_name}: {metric.duration_ms:.2f}ms\n"
    
    report += """
─────────────────────────────────────────────────────────────
Generated by YelpReviewGym Performance Tracker
"""
    
    return report
