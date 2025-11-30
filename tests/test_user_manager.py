"""Unit tests for user management system."""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from yelpreviewgym.user_manager import UserManager


@pytest.fixture
def temp_user_file():
    """Create a temporary file for user data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def user_manager(temp_user_file):
    """Create a UserManager instance with temporary storage."""
    return UserManager(data_file=temp_user_file)


class TestUserCreation:
    """Tests for user creation and retrieval."""
    
    def test_get_or_create_user_new_user(self, user_manager):
        """Test creating a new user."""
        user = user_manager.get_or_create_user("john")
        
        assert user["username"] == "john"
        assert "created_at" in user
        assert user["businesses"] == {}
        assert user["total_attempts"] == 0
        assert user["total_score"] == 0.0
        assert user["badges"] == []
        assert user["certificates"] == []
    
    def test_get_or_create_user_existing_user(self, user_manager):
        """Test retrieving an existing user."""
        # Create user first
        user1 = user_manager.get_or_create_user("john")
        user1["total_attempts"] = 5
        
        # Retrieve same user
        user2 = user_manager.get_or_create_user("john")
        
        assert user2["username"] == "john"
        assert user2["total_attempts"] == 5
    
    def test_user_persistence(self, temp_user_file):
        """Test that user data persists across instances."""
        # Create user with first instance
        manager1 = UserManager(data_file=temp_user_file)
        manager1.get_or_create_user("alice")
        
        # Load with second instance
        manager2 = UserManager(data_file=temp_user_file)
        user = manager2.get_or_create_user("alice")
        
        assert user["username"] == "alice"


class TestBusinessProgress:
    """Tests for business-specific progress tracking."""
    
    def test_save_business_progress(self, user_manager):
        """Test saving progress for a business."""
        user_manager.save_business_progress(
            username="john",
            business_name="Gary Danko",
            location="San Francisco, CA",
            business_type="Restaurant",
            total_scenarios=5,
            completed_scenarios={0, 1, 2},
            scores=[8.5, 9.0, 7.5],
            scenario_titles=["Scenario 1", "Scenario 2", "Scenario 3"]
        )
        
        progress = user_manager.get_business_progress("john", "Gary Danko")
        
        assert progress is not None
        assert progress["location"] == "San Francisco, CA"
        assert progress["business_type"] == "Restaurant"
        assert progress["total_scenarios"] == 5
        assert progress["completed_scenarios"] == [0, 1, 2]
        assert progress["scores"] == [8.5, 9.0, 7.5]
        assert progress["attempts"] == 3
        assert progress["completed"] is False  # Not all scenarios done
    
    def test_save_business_progress_complete(self, user_manager):
        """Test saving complete business progress."""
        user_manager.save_business_progress(
            username="john",
            business_name="Test Restaurant",
            location="NYC",
            business_type="Restaurant",
            total_scenarios=3,
            completed_scenarios={0, 1, 2},
            scores=[8.5, 9.0, 8.5],
            scenario_titles=["S1", "S2", "S3"]
        )
        
        progress = user_manager.get_business_progress("john", "Test Restaurant")
        
        assert progress["completed"] is True  # All scenarios done
    
    def test_get_business_progress_nonexistent(self, user_manager):
        """Test getting progress for non-existent business."""
        progress = user_manager.get_business_progress("john", "Nonexistent")
        assert progress is None
    
    def test_clear_business_progress(self, user_manager):
        """Test clearing progress for a business."""
        # Save progress first
        user_manager.save_business_progress(
            username="john",
            business_name="Test",
            location="NYC",
            business_type="Restaurant",
            total_scenarios=3,
            completed_scenarios={0, 1},
            scores=[8.5, 9.0],
            scenario_titles=["S1", "S2", "S3"]
        )
        
        # Clear progress
        user_manager.clear_business_progress("john", "Test")
        
        progress = user_manager.get_business_progress("john", "Test")
        assert progress is None


class TestCertificates:
    """Tests for certificate management."""
    
    def test_award_certificate(self, user_manager):
        """Test awarding a certificate to a user."""
        user_manager.award_certificate(
            username="john",
            business_name="Gary Danko",
            avg_score=8.5
        )
        
        certs = user_manager.get_user_certificates("john")
        
        assert len(certs) == 1
        assert certs[0]["business_name"] == "Gary Danko"
        assert certs[0]["avg_score"] == 8.5
        assert "date" in certs[0]
        assert "display_date" in certs[0]
    
    def test_award_certificate_update_better_score(self, user_manager):
        """Test updating certificate with better score."""
        # First certificate
        user_manager.award_certificate("john", "Test", 8.0)
        
        # Better certificate
        user_manager.award_certificate("john", "Test", 9.0)
        
        certs = user_manager.get_user_certificates("john")
        
        assert len(certs) == 1  # Still only one cert
        assert certs[0]["avg_score"] == 9.0  # Updated to better score
    
    def test_award_certificate_no_update_worse_score(self, user_manager):
        """Test that worse score doesn't update certificate."""
        # First certificate
        user_manager.award_certificate("john", "Test", 9.0)
        
        # Worse certificate
        user_manager.award_certificate("john", "Test", 8.0)
        
        certs = user_manager.get_user_certificates("john")
        
        assert len(certs) == 1
        assert certs[0]["avg_score"] == 9.0  # Kept better score
    
    def test_multiple_certificates(self, user_manager):
        """Test awarding certificates for different businesses."""
        user_manager.award_certificate("john", "Business 1", 8.5)
        user_manager.award_certificate("john", "Business 2", 9.0)
        user_manager.award_certificate("john", "Business 3", 8.0)
        
        certs = user_manager.get_user_certificates("john")
        
        assert len(certs) == 3
        business_names = [c["business_name"] for c in certs]
        assert "Business 1" in business_names
        assert "Business 2" in business_names
        assert "Business 3" in business_names


class TestUserStats:
    """Tests for user statistics."""
    
    def test_get_user_stats_new_user(self, user_manager):
        """Test getting stats for new user."""
        stats = user_manager.get_user_stats("new_user")
        
        assert stats["total_attempts"] == 0
        assert stats["avg_score"] == 0.0
        assert stats["total_businesses"] == 0
        assert stats["completed_businesses"] == 0
        assert stats["badges"] == []
        assert stats["certificates_count"] == 0
    
    def test_get_user_stats_with_data(self, user_manager):
        """Test getting stats for user with data."""
        # Create user with business progress
        user_manager.save_business_progress(
            username="john",
            business_name="Business 1",
            location="NYC",
            business_type="Restaurant",
            total_scenarios=3,
            completed_scenarios={0, 1, 2},
            scores=[8.5, 9.0, 8.5],
            scenario_titles=["S1", "S2", "S3"]
        )
        
        user_manager.save_business_progress(
            username="john",
            business_name="Business 2",
            location="LA",
            business_type="Restaurant",
            total_scenarios=2,
            completed_scenarios={0},
            scores=[7.5],
            scenario_titles=["S1", "S2"]
        )
        
        user_manager.award_certificate("john", "Business 1", 8.67)
        
        stats = user_manager.get_user_stats("john")
        
        assert stats["total_attempts"] >= 1  # At least one attempt recorded
        assert stats["total_businesses"] == 2
        assert stats["completed_businesses"] == 1  # Only Business 1 is complete
        assert stats["certificates_count"] == 1


class TestLeaderboards:
    """Tests for leaderboard functionality."""
    
    def test_global_leaderboard_empty(self, user_manager):
        """Test global leaderboard with no users."""
        leaderboard = user_manager.get_all_users_leaderboard()
        assert leaderboard == []
    
    def test_global_leaderboard_filters_zero_attempts(self, user_manager):
        """Test that users with 0 attempts don't appear in leaderboard."""
        # Create user but don't add any attempts
        user_manager.get_or_create_user("john")
        
        leaderboard = user_manager.get_all_users_leaderboard()
        
        assert len(leaderboard) == 0  # User not in leaderboard
    
    def test_global_leaderboard_sorting(self, user_manager):
        """Test global leaderboard sorting by score."""
        # Create users with different scores
        user_manager.save_business_progress(
            "alice", "Test", "NYC", "Restaurant", 2, {0, 1}, 
            [9.0, 9.0], ["S1", "S2"]
        )
        user_manager.save_business_progress(
            "bob", "Test", "NYC", "Restaurant", 2, {0, 1},
            [7.0, 7.0], ["S1", "S2"]
        )
        user_manager.save_business_progress(
            "charlie", "Test", "NYC", "Restaurant", 2, {0, 1},
            [8.0, 8.0], ["S1", "S2"]
        )
        
        leaderboard = user_manager.get_all_users_leaderboard()
        
        assert len(leaderboard) == 3
        # Check sorting (highest score first)
        assert leaderboard[0]["username"] == "alice"
        assert leaderboard[1]["username"] == "charlie"
        assert leaderboard[2]["username"] == "bob"
    
    def test_business_leaderboard(self, user_manager):
        """Test business-specific leaderboard."""
        user_manager.save_business_progress(
            "alice", "Gary Danko", "SF", "Restaurant", 3, {0, 1, 2},
            [9.0, 9.0, 9.0], ["S1", "S2", "S3"]
        )
        user_manager.save_business_progress(
            "bob", "Gary Danko", "SF", "Restaurant", 3, {0, 1},
            [7.0, 7.0], ["S1", "S2", "S3"]
        )
        
        leaderboard = user_manager.get_business_leaderboard("Gary Danko")
        
        assert len(leaderboard) == 2
        assert leaderboard[0]["username"] == "alice"
        assert leaderboard[0]["avg_score"] == 9.0
        assert leaderboard[0]["completed"] is True
        assert leaderboard[1]["username"] == "bob"
        assert leaderboard[1]["completed"] is False
    
    def test_get_all_businesses(self, user_manager):
        """Test getting all trained businesses."""
        user_manager.save_business_progress(
            "alice", "Business A", "NYC", "Restaurant", 2, {0},
            [8.0], ["S1", "S2"]
        )
        user_manager.save_business_progress(
            "bob", "Business B", "LA", "Restaurant", 2, {0},
            [8.0], ["S1", "S2"]
        )
        user_manager.save_business_progress(
            "alice", "Business C", "SF", "Restaurant", 2, {0},
            [8.0], ["S1", "S2"]
        )
        
        businesses = user_manager.get_all_businesses()
        
        assert len(businesses) == 3
        assert "Business A" in businesses
        assert "Business B" in businesses
        assert "Business C" in businesses
        assert businesses == sorted(businesses)  # Should be sorted


class TestUserDeletion:
    """Tests for user deletion functionality."""
    
    def test_delete_user(self, user_manager):
        """Test deleting a user."""
        # Create user with data
        user_manager.save_business_progress(
            "john", "Test", "NYC", "Restaurant", 2, {0, 1},
            [8.0, 9.0], ["S1", "S2"]
        )
        user_manager.award_certificate("john", "Test", 8.5)
        
        # Delete user
        result = user_manager.delete_user("john")
        
        assert result is True
        assert "john" not in user_manager.users
        
        # Verify user is gone
        progress = user_manager.get_business_progress("john", "Test")
        assert progress is None
    
    def test_delete_nonexistent_user(self, user_manager):
        """Test deleting a user that doesn't exist."""
        result = user_manager.delete_user("nonexistent")
        assert result is False
    
    def test_delete_user_removes_from_leaderboard(self, user_manager):
        """Test that deleted users don't appear in leaderboard."""
        # Create users
        user_manager.save_business_progress(
            "alice", "Test", "NYC", "Restaurant", 2, {0, 1},
            [9.0, 9.0], ["S1", "S2"]
        )
        user_manager.save_business_progress(
            "bob", "Test", "NYC", "Restaurant", 2, {0, 1},
            [8.0, 8.0], ["S1", "S2"]
        )
        
        # Delete one user
        user_manager.delete_user("alice")
        
        leaderboard = user_manager.get_all_users_leaderboard()
        
        assert len(leaderboard) == 1
        assert leaderboard[0]["username"] == "bob"


class TestSessionLoading:
    """Tests for loading saved sessions."""
    
    def test_load_session_state(self, user_manager):
        """Test loading a saved session."""
        # Save progress
        user_manager.save_business_progress(
            "john", "Test", "NYC", "Restaurant", 3, {0, 1},
            [8.0, 9.0], ["S1", "S2", "S3"]
        )
        
        # Load session
        session = user_manager.load_session_state("john", "Test")
        
        assert session is not None
        assert session["completed_scenarios"] == {0, 1}
        assert session["scores"] == [8.0, 9.0]
        assert session["scenario_titles"] == ["S1", "S2", "S3"]
    
    def test_load_session_state_completed_business(self, user_manager):
        """Test that completed businesses return None for session load."""
        # Save completed progress
        user_manager.save_business_progress(
            "john", "Test", "NYC", "Restaurant", 2, {0, 1},
            [8.0, 9.0], ["S1", "S2"]
        )
        
        # Try to load session
        session = user_manager.load_session_state("john", "Test")
        
        assert session is None  # Already completed
    
    def test_load_session_state_nonexistent(self, user_manager):
        """Test loading session for non-existent business."""
        session = user_manager.load_session_state("john", "Nonexistent")
        assert session is None


class TestDataPersistence:
    """Tests for data persistence and file operations."""
    
    def test_data_file_creation(self, temp_user_file):
        """Test that data file is created."""
        manager = UserManager(data_file=temp_user_file)
        manager.get_or_create_user("test_user")
        
        assert Path(temp_user_file).exists()
    
    def test_data_format(self, temp_user_file):
        """Test that data is saved in correct JSON format."""
        manager = UserManager(data_file=temp_user_file)
        manager.get_or_create_user("test_user")
        
        with open(temp_user_file, encoding='utf-8') as f:
            data = json.load(f)
        
        assert "test_user" in data
        assert isinstance(data["test_user"], dict)
    
    def test_corrupt_file_handling(self, temp_user_file):
        """Test handling of corrupt data file."""
        # Write corrupt data
        with open(temp_user_file, 'w', encoding='utf-8') as f:
            f.write("not valid json{{{")
        
        # Should load without error and return empty dict
        manager = UserManager(data_file=temp_user_file)
        assert manager.users == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
