"""Tests for performance metrics tracking."""

import pytest
import time
from pathlib import Path
import json

from yelpreviewgym.performance_metrics import (
    PerformanceTracker,
    PerformanceMetric,
    track_performance,
    get_tracker,
    format_performance_report,
)


class TestPerformanceMetric:
    """Test PerformanceMetric data model."""
    
    def test_create_metric(self):
        """Test creating a performance metric."""
        metric = PerformanceMetric(
            function_name="test_function",
            start_time=1000.0,
            end_time=1001.5,
            duration_ms=1500.0,
            timestamp="2024-01-01T12:00:00",
            success=True
        )
        
        assert metric.function_name == "test_function"
        assert metric.duration_ms == 1500.0
        assert metric.success is True
        assert metric.error is None


class TestPerformanceTracker:
    """Test PerformanceTracker functionality."""
    
    def test_tracker_initialization(self, tmp_path):
        """Test tracker initialization."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        assert tracker.metrics == []
    
    def test_record_metric(self, tmp_path):
        """Test recording a metric."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        metric = PerformanceMetric(
            function_name="test_func",
            start_time=1000.0,
            end_time=1001.0,
            duration_ms=1000.0,
            timestamp="2024-01-01T12:00:00",
            success=True
        )
        
        tracker.record(metric)
        
        assert len(tracker.metrics) == 1
        assert tracker.metrics[0].function_name == "test_func"
    
    def test_get_stats_single_function(self, tmp_path):
        """Test getting stats for a single function."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        # Add multiple metrics
        for i in range(5):
            metric = PerformanceMetric(
                function_name="test_func",
                start_time=1000.0 + i,
                end_time=1001.0 + i,
                duration_ms=100.0 + i * 10,
                timestamp="2024-01-01T12:00:00",
                success=True
            )
            tracker.record(metric)
        
        stats = tracker.get_stats("test_func")
        
        assert stats["count"] == 5
        assert stats["avg_duration_ms"] == 120.0  # (100 + 110 + 120 + 130 + 140) / 5
        assert stats["min_duration_ms"] == 100.0
        assert stats["max_duration_ms"] == 140.0
        assert stats["success_rate"] == 100.0
    
    def test_get_stats_all_functions(self, tmp_path):
        """Test getting stats for all functions."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        # Add metrics for different functions
        for func in ["func1", "func2"]:
            for i in range(3):
                metric = PerformanceMetric(
                    function_name=func,
                    start_time=1000.0,
                    end_time=1001.0,
                    duration_ms=100.0,
                    timestamp="2024-01-01T12:00:00",
                    success=True
                )
                tracker.record(metric)
        
        stats = tracker.get_stats()
        
        assert stats["count"] == 6
    
    def test_get_recent_metrics(self, tmp_path):
        """Test getting recent metrics."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        # Add 10 metrics
        for i in range(10):
            metric = PerformanceMetric(
                function_name=f"func_{i}",
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=100.0,
                timestamp="2024-01-01T12:00:00",
                success=True
            )
            tracker.record(metric)
        
        recent = tracker.get_recent_metrics(limit=3)
        
        assert len(recent) == 3
        assert recent[-1].function_name == "func_9"
    
    def test_clear_metrics(self, tmp_path):
        """Test clearing all metrics."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        metric = PerformanceMetric(
            function_name="test_func",
            start_time=1000.0,
            end_time=1001.0,
            duration_ms=1000.0,
            timestamp="2024-01-01T12:00:00",
            success=True
        )
        tracker.record(metric)
        
        assert len(tracker.metrics) == 1
        
        tracker.clear_metrics()
        
        assert len(tracker.metrics) == 0


class TestTrackPerformanceDecorator:
    """Test track_performance decorator."""
    
    def test_decorator_basic(self):
        """Test basic decorator usage."""
        @track_performance
        def sample_function():
            time.sleep(0.01)
            return "result"
        
        result = sample_function()
        
        assert result == "result"
        
        # Check that metric was recorded
        tracker = get_tracker()
        assert len(tracker.metrics) > 0
        
        # Find our metric
        metric = None
        for m in tracker.metrics:
            if m.function_name == "sample_function":
                metric = m
                break
        
        assert metric is not None
        assert metric.success is True
        assert metric.duration_ms >= 10.0  # Should be at least 10ms
    
    def test_decorator_with_metadata(self):
        """Test decorator with metadata."""
        @track_performance(metadata={"api": "test"})
        def api_function():
            return "api_result"
        
        result = api_function()
        
        assert result == "api_result"
        
        tracker = get_tracker()
        metric = None
        for m in tracker.metrics:
            if m.function_name == "api_function":
                metric = m
                break
        
        assert metric is not None
        assert metric.metadata.get("api") == "test"
    
    def test_decorator_with_exception(self):
        """Test decorator when function raises exception."""
        @track_performance
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        tracker = get_tracker()
        metric = None
        for m in tracker.metrics:
            if m.function_name == "failing_function":
                metric = m
                break
        
        assert metric is not None
        assert metric.success is False
        assert "Test error" in metric.error


class TestFormatPerformanceReport:
    """Test performance report formatting."""
    
    def test_format_report(self, tmp_path):
        """Test formatting performance report."""
        save_path = tmp_path / "test_metrics.json"
        tracker = PerformanceTracker(save_path=str(save_path))
        
        # Add some metrics
        for i in range(3):
            metric = PerformanceMetric(
                function_name="test_func",
                start_time=1000.0,
                end_time=1001.0,
                duration_ms=100.0,
                timestamp="2024-01-01T12:00:00",
                success=True
            )
            tracker.record(metric)
        
        report = format_performance_report(tracker)
        
        assert "PERFORMANCE REPORT" in report
        assert "OVERALL STATISTICS" in report
        assert "test_func" in report
        assert "3" in report  # count
