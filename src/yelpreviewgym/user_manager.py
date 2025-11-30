"""User management and progress tracking system."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UserManager:
    """Manage user profiles and training progress."""
    
    def __init__(self, data_file: str = "user_data.json"):
        """Initialize the user manager.
        
        Args:
            data_file: Path to the JSON file storing user data
        """
        self.data_file = Path(data_file)
        self.users: Dict[str, Dict[str, Any]] = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """Load user data from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_data(self) -> None:
        """Save user data to JSON file."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=2)
        except IOError as e:
            print(f"Error saving user data: {e}")
    
    def get_or_create_user(self, username: str) -> Dict[str, Any]:
        """Get existing user or create new user profile.
        
        Args:
            username: Unique username
            
        Returns:
            User profile dictionary
        """
        if username not in self.users:
            self.users[username] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "businesses": {},  # business_name -> progress data
                "total_attempts": 0,
                "total_score": 0.0,
                "badges": [],
                "certificates": []
            }
            self._save_data()
        return self.users[username]
    
    def get_business_progress(self, username: str, business_name: str) -> Optional[Dict[str, Any]]:
        """Get user's progress for a specific business.
        
        Args:
            username: Username
            business_name: Business name
            
        Returns:
            Business progress data or None if not found
        """
        user = self.get_or_create_user(username)
        return user["businesses"].get(business_name)
    
    def save_business_progress(
        self,
        username: str,
        business_name: str,
        location: str,
        business_type: str,
        total_scenarios: int,
        completed_scenarios: set,
        scores: List[float],
        scenario_titles: List[str]
    ) -> None:
        """Save user's progress for a business.
        
        Args:
            username: Username
            business_name: Business name
            location: Business location
            business_type: Type of business
            total_scenarios: Total number of scenarios
            completed_scenarios: Set of completed scenario indices
            scores: List of scores achieved
            scenario_titles: List of scenario titles
        """
        user = self.get_or_create_user(username)
        
        if business_name not in user["businesses"]:
            user["businesses"][business_name] = {
                "location": location,
                "business_type": business_type,
                "started_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_scenarios": total_scenarios,
                "completed_scenarios": [],
                "scores": [],
                "scenario_titles": scenario_titles,
                "attempts": 0,
                "completed": False
            }
        
        business_data = user["businesses"][business_name]
        business_data["last_updated"] = datetime.now().isoformat()
        business_data["total_scenarios"] = total_scenarios
        business_data["completed_scenarios"] = sorted(list(completed_scenarios))
        business_data["scores"] = scores
        business_data["scenario_titles"] = scenario_titles
        business_data["attempts"] = len(scores)
        business_data["completed"] = len(completed_scenarios) == total_scenarios
        
        # Update overall stats
        user["total_attempts"] += 1
        if scores:
            user["total_score"] += scores[-1]  # Add latest score
        
        self._save_data()
    
    def award_certificate(self, username: str, business_name: str, avg_score: float) -> None:
        """Award a completion certificate to user.
        
        Args:
            username: Username
            business_name: Business name
            avg_score: Average score achieved
        """
        user = self.get_or_create_user(username)
        
        cert = {
            "business_name": business_name,
            "avg_score": avg_score,
            "date": datetime.now().isoformat(),
            "display_date": datetime.now().strftime("%B %d, %Y")
        }
        
        # Check if certificate already exists for this business
        existing = [c for c in user["certificates"] if c["business_name"] == business_name]
        if existing:
            # Update if new score is better
            if avg_score > existing[0]["avg_score"]:
                user["certificates"].remove(existing[0])
                user["certificates"].append(cert)
        else:
            user["certificates"].append(cert)
        
        self._save_data()
    
    def get_user_certificates(self, username: str) -> List[Dict[str, Any]]:
        """Get all certificates earned by user.
        
        Args:
            username: Username
            
        Returns:
            List of certificate data
        """
        user = self.get_or_create_user(username)
        return user["certificates"]
    
    def get_user_stats(self, username: str) -> Dict[str, Any]:
        """Get overall user statistics.
        
        Args:
            username: Username
            
        Returns:
            Dictionary with user stats
        """
        user = self.get_or_create_user(username)
        
        total_businesses = len(user["businesses"])
        completed_businesses = sum(
            1 for b in user["businesses"].values() if b.get("completed", False)
        )
        
        avg_score = 0.0
        if user["total_attempts"] > 0:
            avg_score = user["total_score"] / user["total_attempts"]
        
        return {
            "total_attempts": user["total_attempts"],
            "avg_score": avg_score,
            "total_businesses": total_businesses,
            "completed_businesses": completed_businesses,
            "badges": user["badges"],
            "certificates_count": len(user["certificates"])
        }
    
    def load_session_state(self, username: str, business_name: str) -> Optional[Dict[str, Any]]:
        """Load saved session state for resuming training.
        
        Args:
            username: Username
            business_name: Business name
            
        Returns:
            Session state data or None if no saved progress
        """
        progress = self.get_business_progress(username, business_name)
        if not progress:
            return None
        
        # Don't load if already completed
        if progress.get("completed", False):
            return None
        
        return {
            "completed_scenarios": set(progress["completed_scenarios"]),
            "scores": progress["scores"],
            "scenario_titles": progress["scenario_titles"]
        }
    
    def clear_business_progress(self, username: str, business_name: str) -> None:
        """Clear progress for a specific business (restart training).
        
        Args:
            username: Username
            business_name: Business name
        """
        user = self.get_or_create_user(username)
        if business_name in user["businesses"]:
            del user["businesses"][business_name]
            self._save_data()
    
    def delete_user(self, username: str) -> bool:
        """Delete a user completely from the system.
        
        Args:
            username: Username to delete
            
        Returns:
            True if user was deleted, False if user didn't exist
        """
        if username in self.users:
            del self.users[username]
            self._save_data()
            return True
        return False
    
    def get_all_users_leaderboard(self) -> List[Dict[str, Any]]:
        """Get leaderboard data for all users.
        
        Returns:
            List of user data sorted by performance (only users with attempts)
        """
        leaderboard = []
        for username in self.users.keys():
            stats = self.get_user_stats(username)
            # Only include users who have actually trained (attempts > 0)
            if stats["total_attempts"] > 0:
                leaderboard.append({
                    "username": username,
                    "total_attempts": stats["total_attempts"],
                    "avg_score": stats["avg_score"],
                    "completed_businesses": stats["completed_businesses"],
                    "certificates": stats["certificates_count"]
                })
        
        # Sort by average score (descending)
        leaderboard.sort(key=lambda x: x["avg_score"], reverse=True)
        return leaderboard
    
    def get_business_leaderboard(self, business_name: str) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific business.
        
        Args:
            business_name: Name of the business
            
        Returns:
            List of user performance data for that business, sorted by average score
        """
        leaderboard = []
        for username, user_data in self.users.items():
            if business_name in user_data.get("businesses", {}):
                business_data = user_data["businesses"][business_name]
                
                # Calculate average score for this business
                avg_score = 0.0
                if business_data.get("scores"):
                    avg_score = sum(business_data["scores"]) / len(business_data["scores"])
                
                leaderboard.append({
                    "username": username,
                    "avg_score": avg_score,
                    "attempts": business_data.get("attempts", 0),
                    "completed_scenarios": len(business_data.get("completed_scenarios", [])),
                    "total_scenarios": business_data.get("total_scenarios", 0),
                    "completed": business_data.get("completed", False),
                    "last_updated": business_data.get("last_updated", "")
                })
        
        # Sort by average score (descending), then by completion
        leaderboard.sort(key=lambda x: (x["avg_score"], x["completed"]), reverse=True)
        return leaderboard
    
    def get_all_businesses(self) -> List[str]:
        """Get list of all businesses that have been trained on.
        
        Returns:
            List of unique business names
        """
        businesses = set()
        for user_data in self.users.values():
            businesses.update(user_data.get("businesses", {}).keys())
        return sorted(list(businesses))
