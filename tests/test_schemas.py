"""Tests for data models and schemas."""

import pytest
from datetime import datetime

from yelpreviewgym.schemas import (
    BusinessInsights,
    DialogueTurn,
    TrainingScenario,
    FeedbackResult,
    TrainingSession,
)


class TestBusinessInsights:
    """Test BusinessInsights data model."""
    
    def test_create_basic_insights(self):
        """Test creating basic business insights."""
        insights = BusinessInsights(
            delights=["Great food", "Excellent service"],
            pains=["Long wait times", "Noisy environment"],
            personas=["Family diners", "Business professionals"]
        )
        
        assert len(insights.delights) == 2
        assert len(insights.pains) == 2
        assert len(insights.personas) == 2
        assert insights.delights[0] == "Great food"
    
    def test_empty_insights(self):
        """Test creating insights with empty lists."""
        insights = BusinessInsights(
            delights=[],
            pains=[],
            personas=[]
        )
        
        assert insights.delights == []
        assert insights.pains == []
        assert insights.personas == []
    
    def test_optional_fields(self):
        """Test optional fields in BusinessInsights."""
        insights = BusinessInsights(
            delights=["Great food"],
            pains=["Slow service"],
            personas=["Foodies"],
            competitor_insights=["Better than Joe's Pizza"],
            review_sentiment_score=8.5
        )
        
        assert insights.competitor_insights == ["Better than Joe's Pizza"]
        assert insights.review_sentiment_score == 8.5


class TestDialogueTurn:
    """Test DialogueTurn data model."""
    
    def test_create_dialogue_turn(self):
        """Test creating a dialogue turn."""
        turn = DialogueTurn(
            speaker="Customer",
            text="The food was cold!"
        )
        
        assert turn.speaker == "Customer"
        assert turn.text == "The food was cold!"
    
    def test_staff_dialogue(self):
        """Test staff response dialogue."""
        turn = DialogueTurn(
            speaker="Staff",
            text="I apologize for that. Let me get you a fresh meal."
        )
        
        assert turn.speaker == "Staff"
        assert "apologize" in turn.text


class TestTrainingScenario:
    """Test TrainingScenario data model."""
    
    def test_create_basic_scenario(self):
        """Test creating a training scenario."""
        scenario = TrainingScenario(
            title="Cold Food Complaint",
            pain_summary="Customer received cold food",
            bad_dialogue=[
                DialogueTurn(speaker="Customer", text="My food is cold!"),
                DialogueTurn(speaker="Staff", text="That's not my problem.")
            ],
            good_dialogue=[
                DialogueTurn(speaker="Customer", text="My food is cold!"),
                DialogueTurn(speaker="Staff", text="I'm so sorry! Let me fix that right away.")
            ]
        )
        
        assert scenario.title == "Cold Food Complaint"
        assert len(scenario.bad_dialogue) == 2
        assert len(scenario.good_dialogue) == 2
        assert scenario.difficulty_level == "medium"  # default value
        assert scenario.estimated_time_minutes == 5  # default value
    
    def test_scenario_with_custom_difficulty(self):
        """Test scenario with custom difficulty."""
        scenario = TrainingScenario(
            title="Angry Customer Escalation",
            pain_summary="Customer demanding refund",
            bad_dialogue=[],
            good_dialogue=[],
            difficulty_level="hard",
            estimated_time_minutes=10
        )
        
        assert scenario.difficulty_level == "hard"
        assert scenario.estimated_time_minutes == 10


class TestFeedbackResult:
    """Test FeedbackResult data model."""
    
    def test_create_feedback(self):
        """Test creating feedback result."""
        feedback = FeedbackResult(
            score=8.5,
            summary="Good response with empathy",
            strengths=["Showed empathy", "Offered solution"],
            improvements=["Could be more specific", "Add timeframe"]
        )
        
        assert feedback.score == 8.5
        assert len(feedback.strengths) == 2
        assert len(feedback.improvements) == 2
    
    def test_feedback_with_optional_fields(self):
        """Test feedback with optional fields."""
        feedback = FeedbackResult(
            score=9.5,
            summary="Excellent response",
            strengths=["Perfect empathy"],
            improvements=[],
            recommended_next_steps=["Practice harder scenarios"],
            badges_earned=["Perfect Score", "High Achiever"]
        )
        
        assert feedback.score == 9.5
        assert len(feedback.badges_earned) == 2
        assert feedback.recommended_next_steps[0] == "Practice harder scenarios"
    
    def test_feedback_without_score(self):
        """Test feedback can have None score."""
        feedback = FeedbackResult(
            score=None,
            summary="Unable to parse response",
            strengths=[],
            improvements=[]
        )
        
        assert feedback.score is None
        assert feedback.summary == "Unable to parse response"


class TestTrainingSession:
    """Test TrainingSession data model."""
    
    def test_create_training_session(self):
        """Test creating a training session."""
        session = TrainingSession(
            business_name="Joe's Pizza",
            timestamp=datetime.now(),
            scenarios_practiced=5,
            average_score=8.2,
            improvement_over_time=[7.0, 7.5, 8.0, 8.5, 9.0],
            time_spent_minutes=25
        )
        
        assert session.business_name == "Joe's Pizza"
        assert session.scenarios_practiced == 5
        assert session.average_score == 8.2
        assert len(session.improvement_over_time) == 5
        assert session.time_spent_minutes == 25
