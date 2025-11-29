"""Enhanced Features for YelpReviewGym

Enterprise-grade features including progress tracking, leaderboard,
certification system, and comprehensive reporting.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class ProgressTracker:
    """Track user progress and achievements."""
    
    def __init__(self, save_path: str = "training_progress.json"):
        self.save_path = Path(save_path)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing progress data."""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"sessions": [], "total_score": 0, "badges": []}
        return {"sessions": [], "total_score": 0, "badges": []}
    
    def _save_data(self):
        """Save progress data."""
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except (IOError, TypeError):
            pass
    
    def record_attempt(self, business: str, scenario: str, score: float):
        """Record a training attempt."""
        session = {
            "timestamp": datetime.now().isoformat(),
            "business": business,
            "scenario": scenario,
            "score": score
        }
        self.data["sessions"].append(session)
        self.data["total_score"] = self.get_average_score()
        
        self._check_badges()
        
        self._save_data()
    
    def get_average_score(self) -> float:
        """Calculate average score across all attempts."""
        if not self.data["sessions"]:
            return 0.0
        scores = [s["score"] for s in self.data["sessions"] if s.get("score")]
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_total_attempts(self) -> int:
        """Get total number of practice attempts."""
        return len(self.data["sessions"])
    
    def get_improvement_trend(self, last_n: int = 10) -> List[float]:
        """Get score trend for last N attempts."""
        sessions = self.data["sessions"][-last_n:]
        return [s.get("score", 0.0) for s in sessions]
    
    def _check_badges(self):
        """Check and award badges based on achievements."""
        badges = self.data.get("badges", [])
        attempts = self.get_total_attempts()
        avg_score = self.get_average_score()
        
        if attempts >= 1 and "First Steps" not in badges:
            badges.append("First Steps")
        
        if attempts >= 10 and "Practice Makes Perfect" not in badges:
            badges.append("Practice Makes Perfect")
        
        if attempts >= 50 and "Master Trainer" not in badges:
            badges.append("Master Trainer")
        
        if avg_score >= 8.0 and attempts >= 5 and "High Achiever" not in badges:
            badges.append("High Achiever")
        
        recent_perfect = any(s.get("score", 0) >= 9.5 for s in self.data["sessions"][-5:])
        if recent_perfect and "Perfect Score" not in badges:
            badges.append("Perfect Score")
        
        self.data["badges"] = badges
    
    def get_badges(self) -> List[str]:
        """Get earned badges."""
        return self.data.get("badges", [])


class LeaderboardManager:
    """Manage leaderboard for multiple users/staff."""
    
    def __init__(self, save_path: str = "leaderboard.json"):
        self.save_path = Path(save_path)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load leaderboard data."""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"users": []}
        return {"users": []}
    
    def _save_data(self):
        """Save leaderboard data."""
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except (IOError, TypeError):
            pass
    
    def update_user_score(self, username: str, score: float, scenario: str = ""):
        """Update user's score on leaderboard.
        
        Args:
            username: Username to update
            score: Score to record
            scenario: Scenario name (optional, for logging purposes)
        """
        users = self.data.get("users", [])
        
        user = None
        for u in users:
            if u["username"] == username:
                user = u
                break
        
        if not user:
            user = {
                "username": username,
                "total_attempts": 0,
                "best_score": 0.0,
                "average_score": 0.0,
                "scores": []
            }
            users.append(user)
        
        user["total_attempts"] += 1
        user["scores"].append(score)
        user["best_score"] = max(user["best_score"], score)
        user["average_score"] = sum(user["scores"]) / len(user["scores"])
        
        users.sort(key=lambda x: x["average_score"], reverse=True)
        
        self.data["users"] = users
        self._save_data()
    
    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        """Get top performers."""
        users = self.data.get("users", [])
        return users[:limit]


class CertificationSystem:
    """Issue training certificates based on performance."""
    
    @staticmethod
    def check_certification_eligibility(
        total_attempts: int,
        average_score: float,
        badges: List[str]
    ) -> Dict:
        """Check if user is eligible for certification."""
        result = {
            "eligible": False,
            "level": None,
            "requirements_met": [],
            "requirements_needed": []
        }
        
        if total_attempts >= 10 and average_score >= 6.0:
            result["eligible"] = True
            result["level"] = "Bronze"
            result["requirements_met"] = [
                f"Completed {total_attempts} practice sessions",
                f"Achieved {average_score:.1f} average score"
            ]
        
        if total_attempts >= 25 and average_score >= 7.5 and len(badges) >= 3:
            result["level"] = "Silver"
            result["requirements_met"].append(f"Earned {len(badges)} badges")
        
        if total_attempts >= 50 and average_score >= 8.5 and len(badges) >= 5:
            result["level"] = "Gold"
        
        if not result["eligible"]:
            if total_attempts < 10:
                result["requirements_needed"].append(f"Need {10 - total_attempts} more practice sessions")
            if average_score < 6.0:
                result["requirements_needed"].append(f"Need {6.0 - average_score:.1f} points higher average score")
        
        return result
    
    @staticmethod
    def generate_certificate_text(
        username: str,
        level: str,
        business_name: str,
        date: str
    ) -> str:
        """Generate certificate text."""
        return f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              YELP REVIEW GYM CERTIFICATE                ║
║                                                          ║
║                    {level.upper()} LEVEL                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

This certifies that

    {username.upper()}

has successfully completed customer service training
for {business_name} and demonstrated excellence in:

    ✓ Empathetic customer communication
    ✓ Problem-solving and conflict resolution
    ✓ Professional service delivery

Awarded on: {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """


class ReportGenerator:
    """Generate training reports and analytics."""
    
    @staticmethod
    def generate_session_report(
        business_name: str,
        insights: Dict,
        scenarios_count: int,
        scores: List[float],
        time_spent: int
    ) -> str:
        """Generate training session report."""
        avg_score = sum(scores) / len(scores) if scores else 0
        
        report = f"""
═══════════════════════════════════════════════════════════════
           YELP REVIEW GYM - TRAINING SESSION REPORT
═══════════════════════════════════════════════════════════════

Business: {business_name}
Date: {datetime.now().strftime('%B %d, %Y')}
Session Duration: {time_spent} minutes

─────────────────────────────────────────────────────────────

📊 PERFORMANCE SUMMARY

Scenarios Practiced: {scenarios_count}
Average Score: {avg_score:.1f}/10
"""
        
        if scores:
            report += "\nScore Breakdown:\n"
            for i, score in enumerate(scores, 1):
                stars = "⭐" * int(score)
                report += f"  Attempt {i}: {score:.1f}/10 {stars}\n"
        
        if len(scores) >= 2:
            trend = scores[-1] - scores[0]
            if trend > 0:
                report += f"\n📈 Improvement: +{trend:.1f} points (Great progress!)\n"
            elif trend < 0:
                report += f"\n📉 Trend: {trend:.1f} points (Keep practicing!)\n"
            else:
                report += "\n➡️  Consistent performance\n"
        
        report += """
─────────────────────────────────────────────────────────────

🎯 KEY FOCUS AREAS

Customer Pain Points Addressed:
"""
        if insights and "pains" in insights:
            for pain in insights["pains"][:3]:
                report += f"  • {pain}\n"
        
        report += """
─────────────────────────────────────────────────────────────

💡 RECOMMENDATIONS

"""
        if avg_score >= 8.5:
            report += "  ✅ Excellent work! Ready for real customer interactions.\n"
            report += "  ✅ Consider mentoring other staff members.\n"
        elif avg_score >= 7.0:
            report += "  👍 Good progress! Practice 2-3 more scenarios.\n"
            report += "  👍 Focus on empathy and solution-oriented responses.\n"
        else:
            report += "  📚 More practice needed. Review good examples carefully.\n"
            report += "  📚 Try easier scenarios first to build confidence.\n"
        
        report += """
─────────────────────────────────────────────────────────────

Generated by YelpReviewGym
Built with Yelp AI API
═══════════════════════════════════════════════════════════════
"""
        return report
    
    @staticmethod
    def export_to_file(report: str, filename: str):
        """Export report to text file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except (IOError, OSError):
            return False


def calculate_difficulty(scenario_title: str, pain_summary: str) -> str:
    """Estimate difficulty level of a scenario."""
    # Simple heuristic based on keywords
    hard_keywords = ["complaint", "angry", "refund", "frustrated", "disappointed"]
    easy_keywords = ["question", "info", "help", "clarify"]
    
    text = (scenario_title + " " + pain_summary).lower()
    
    if any(keyword in text for keyword in hard_keywords):
        return "hard"
    elif any(keyword in text for keyword in easy_keywords):
        return "easy"
    else:
        return "medium"


def award_badges_for_score(score: float) -> List[str]:
    """Award badges based on score."""
    badges = []
    
    if score >= 9.5:
        badges.append("🏆 Perfect Response")
    elif score >= 8.5:
        badges.append("⭐ Excellent Service")
    elif score >= 7.5:
        badges.append("👍 Good Effort")
    
    return badges
