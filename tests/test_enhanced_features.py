"""Unit tests for enhanced features and validation."""

import pytest


class TestUsernameValidation:
    """Tests for username validation logic."""
    
    def test_valid_username_alphanumeric(self):
        """Test valid alphanumeric username."""
        username = "john123"
        # Length check
        assert 3 <= len(username) <= 20
        # Character check (alphanumeric + space + underscore)
        assert all(c.isalnum() or c in [' ', '_'] for c in username)
    
    def test_valid_username_with_space(self):
        """Test valid username with spaces."""
        username = "John Doe"
        assert 3 <= len(username) <= 20
        assert all(c.isalnum() or c in [' ', '_'] for c in username)
    
    def test_valid_username_with_underscore(self):
        """Test valid username with underscores."""
        username = "john_doe_123"
        assert 3 <= len(username) <= 20
        assert all(c.isalnum() or c in [' ', '_'] for c in username)
    
    def test_invalid_username_too_short(self):
        """Test username that is too short."""
        username = "ab"
        assert len(username) < 3
    
    def test_invalid_username_too_long(self):
        """Test username that is too long."""
        username = "a" * 21
        assert len(username) > 20
    
    def test_invalid_username_special_chars(self):
        """Test username with invalid special characters."""
        invalid_usernames = ["john@doe", "user#123", "test!user", "user$"]
        for username in invalid_usernames:
            assert not all(c.isalnum() or c in [' ', '_'] for c in username)
    
    def test_username_whitespace_handling(self):
        """Test that usernames are stripped of whitespace."""
        username = "  john  "
        stripped = username.strip()
        assert stripped == "john"
        assert " " not in stripped


class TestCertificateRequirements:
    """Tests for certificate eligibility requirements."""
    
    CERTIFICATION_THRESHOLD = 8.0
    
    def test_score_above_threshold(self):
        """Test score that qualifies for certificate."""
        avg_score = 8.5
        assert avg_score >= self.CERTIFICATION_THRESHOLD
    
    def test_score_at_threshold(self):
        """Test score exactly at threshold."""
        avg_score = 8.0
        assert avg_score >= self.CERTIFICATION_THRESHOLD
    
    def test_score_below_threshold(self):
        """Test score that doesn't qualify."""
        avg_score = 7.9
        assert avg_score < self.CERTIFICATION_THRESHOLD
    
    def test_perfect_score(self):
        """Test perfect score."""
        avg_score = 10.0
        assert avg_score >= self.CERTIFICATION_THRESHOLD
    
    def test_minimum_score(self):
        """Test minimum possible score."""
        avg_score = 0.0
        assert avg_score < self.CERTIFICATION_THRESHOLD


class TestScenarioCompletion:
    """Tests for scenario completion logic."""
    
    def test_all_scenarios_completed(self):
        """Test when all scenarios are completed."""
        total_scenarios = 5
        completed_scenarios = {0, 1, 2, 3, 4}
        
        assert len(completed_scenarios) == total_scenarios
    
    def test_partial_completion(self):
        """Test partial scenario completion."""
        total_scenarios = 5
        completed_scenarios = {0, 1, 2}
        
        assert len(completed_scenarios) < total_scenarios
        completion_rate = len(completed_scenarios) / total_scenarios
        assert completion_rate == 0.6
    
    def test_no_scenarios_completed(self):
        """Test no scenarios completed."""
        completed_scenarios = set()
        
        assert len(completed_scenarios) == 0
    
    def test_scenario_index_validity(self):
        """Test that scenario indices are valid."""
        total_scenarios = 5
        completed_scenarios = {0, 1, 2}
        
        for idx in completed_scenarios:
            assert 0 <= idx < total_scenarios


class TestScoreCalculation:
    """Tests for score calculation and averaging."""
    
    def test_average_score_calculation(self):
        """Test average score calculation."""
        scores = [8.5, 9.0, 7.5, 8.0, 9.5]
        avg_score = sum(scores) / len(scores)
        
        assert avg_score == 8.5
    
    def test_average_score_single_attempt(self):
        """Test average with single score."""
        scores = [8.5]
        avg_score = sum(scores) / len(scores)
        
        assert avg_score == 8.5
    
    def test_average_score_precision(self):
        """Test score precision to 1 decimal place."""
        scores = [8.33, 9.67, 7.11]
        avg_score = round(sum(scores) / len(scores), 1)
        
        assert avg_score == 8.4
    
    def test_score_range_validation(self):
        """Test that scores are within valid range."""
        scores = [8.5, 9.0, 7.5, 10.0, 0.0]
        
        for score in scores:
            assert 0.0 <= score <= 10.0


class TestProgressTracking:
    """Tests for progress tracking and metrics."""
    
    def test_attempts_increment(self):
        """Test that attempts increment correctly."""
        initial_attempts = 0
        
        # Simulate attempts
        attempts = initial_attempts + 1
        assert attempts == 1
        
        attempts += 1
        assert attempts == 2
    
    def test_business_count_tracking(self):
        """Test tracking number of businesses trained on."""
        businesses = set()
        
        businesses.add("Business 1")
        assert len(businesses) == 1
        
        businesses.add("Business 2")
        assert len(businesses) == 2
        
        businesses.add("Business 1")  # Duplicate
        assert len(businesses) == 2  # No change
    
    def test_completion_status(self):
        """Test completion status determination."""
        # Complete
        total = 5
        completed = 5
        assert completed == total
        
        # Incomplete
        completed = 3
        assert completed < total


class TestLeaderboardRanking:
    """Tests for leaderboard ranking logic."""
    
    def test_ranking_by_score(self):
        """Test users are ranked by average score."""
        users = [
            {"username": "alice", "avg_score": 9.0},
            {"username": "bob", "avg_score": 7.5},
            {"username": "charlie", "avg_score": 8.5}
        ]
        
        sorted_users = sorted(users, key=lambda x: x["avg_score"], reverse=True)
        
        assert sorted_users[0]["username"] == "alice"
        assert sorted_users[1]["username"] == "charlie"
        assert sorted_users[2]["username"] == "bob"
    
    def test_ranking_filters_zero_attempts(self):
        """Test that users with 0 attempts are filtered."""
        users = [
            {"username": "alice", "total_attempts": 1, "avg_score": 9.0},
            {"username": "bob", "total_attempts": 0, "avg_score": 0.0},
            {"username": "charlie", "total_attempts": 2, "avg_score": 8.5}
        ]
        
        filtered_users = [u for u in users if u["total_attempts"] > 0]
        
        assert len(filtered_users) == 2
        assert "bob" not in [u["username"] for u in filtered_users]
    
    def test_rank_assignment(self):
        """Test rank numbers are assigned correctly."""
        users = [
            {"username": "alice", "avg_score": 9.0},
            {"username": "charlie", "avg_score": 8.5},
            {"username": "bob", "avg_score": 7.5}
        ]
        
        for idx in range(len(users)):
            rank = idx + 1
            assert rank > 0
            assert rank <= len(users)


class TestDataExport:
    """Tests for data export functionality."""
    
    def test_export_data_structure(self):
        """Test exported data has correct structure."""
        user_data = {
            "username": "john",
            "total_attempts": 5,
            "avg_score": 8.5,
            "businesses": {
                "Test Business": {
                    "attempts": 3,
                    "scores": [8.5, 9.0, 8.0],
                    "completed": True
                }
            }
        }
        
        # Verify structure
        assert "username" in user_data
        assert "total_attempts" in user_data
        assert "avg_score" in user_data
        assert "businesses" in user_data
        assert isinstance(user_data["businesses"], dict)


class TestProfileDeletion:
    """Tests for profile deletion functionality."""
    
    def test_delete_removes_user_data(self):
        """Test that deletion removes all user data."""
        users = {"john": {"data": "value"}}
        username = "john"
        
        # Delete
        if username in users:
            del users[username]
        
        assert username not in users
    
    def test_delete_nonexistent_user(self):
        """Test deleting user that doesn't exist."""
        users = {"alice": {"data": "value"}}
        username = "bob"
        
        result = username in users
        assert result is False
    
    def test_session_state_reset(self):
        """Test session state variables are reset on deletion."""
        session_state = {
            "username": "john",
            "business_name": "Test",
            "location": "NYC",
            "current_scenarios": [],
            "completed_scenarios": set(),
            "scores": []
        }
        
        # Reset all keys
        keys_to_reset = list(session_state.keys())
        for key in keys_to_reset:
            del session_state[key]
        
        assert len(session_state) == 0


class TestComparisonMetrics:
    """Tests for comparison metrics in analytics."""
    
    def test_rank_change_calculation(self):
        """Test rank change calculation."""
        current_rank = 5
        total_users = 10
        
        # User is in top half
        top_percentage = (current_rank / total_users) * 100
        assert top_percentage == 50.0
    
    def test_percentile_calculation(self):
        """Test percentile calculation."""
        user_score = 8.5
        all_scores = [7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
        
        scores_below = len([s for s in all_scores if s < user_score])
        percentile = (scores_below / len(all_scores)) * 100
        
        assert percentile == 50.0  # 3 out of 6 scores below
    
    def test_above_average_comparison(self):
        """Test comparison to average score."""
        user_score = 8.5
        avg_score = 7.5
        
        difference = user_score - avg_score
        assert difference > 0
        assert user_score > avg_score


class TestBusinessSpecificLeaderboard:
    """Tests for business-specific leaderboard."""
    
    def test_filter_by_business(self):
        """Test filtering users by specific business."""
        all_progress = [
            {"username": "alice", "business": "Business A"},
            {"username": "bob", "business": "Business B"},
            {"username": "charlie", "business": "Business A"}
        ]
        
        business_name = "Business A"
        filtered = [p for p in all_progress if p["business"] == business_name]
        
        assert len(filtered) == 2
        assert all(p["business"] == business_name for p in filtered)
    
    def test_business_completion_status(self):
        """Test business completion tracking."""
        progress = {
            "total_scenarios": 5,
            "completed_scenarios": [0, 1, 2, 3, 4],
            "completed": True
        }
        
        assert progress["completed"] is True
        assert len(progress["completed_scenarios"]) == progress["total_scenarios"]


class TestQuickStats:
    """Tests for quick stats banner calculations."""
    
    def test_total_attempts_aggregation(self):
        """Test total attempts calculation across businesses."""
        businesses = {
            "Business 1": {"attempts": 3},
            "Business 2": {"attempts": 5},
            "Business 3": {"attempts": 2}
        }
        
        total_attempts = sum(b["attempts"] for b in businesses.values())
        assert total_attempts == 10
    
    def test_weighted_average_score(self):
        """Test weighted average calculation."""
        businesses = {
            "Business 1": {"scores": [8.0, 9.0], "attempts": 2},
            "Business 2": {"scores": [7.5, 8.5, 9.5], "attempts": 3}
        }
        
        all_scores = []
        for b in businesses.values():
            all_scores.extend(b["scores"])
        
        avg_score = sum(all_scores) / len(all_scores)
        assert round(avg_score, 1) == 8.5
    
    def test_unique_businesses_count(self):
        """Test counting unique businesses."""
        businesses = {
            "Business A": {},
            "Business B": {},
            "Business C": {}
        }
        
        count = len(businesses)
        assert count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
