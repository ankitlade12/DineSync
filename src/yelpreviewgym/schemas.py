"""Data Models for YelpReviewGym

Defines structured data types for business insights, training scenarios,
feedback results, and session tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class BusinessInsights:
    """Business analysis from Yelp reviews."""
    
    delights: List[str]
    pains: List[str]
    personas: List[str]
    competitor_insights: List[str] = field(default_factory=list)
    review_sentiment_score: Optional[float] = None


@dataclass
class DialogueTurn:
    """Single turn in a conversation."""
    
    speaker: str
    text: str


@dataclass
class TrainingScenario:
    """Practice scenario for staff training."""
    
    title: str
    pain_summary: str
    bad_dialogue: List[DialogueTurn]
    good_dialogue: List[DialogueTurn]
    difficulty_level: str = "medium"
    estimated_time_minutes: int = 5


@dataclass
class FeedbackResult:
    """AI evaluation of staff response."""
    
    score: Optional[float]
    summary: str
    strengths: List[str]
    improvements: List[str]
    recommended_next_steps: List[str] = field(default_factory=list)
    badges_earned: List[str] = field(default_factory=list)


@dataclass
class TrainingSession:
    """Complete training session for analytics."""
    
    business_name: str
    timestamp: datetime
    scenarios_practiced: int
    average_score: float
    improvement_over_time: List[float]

    time_spent_minutes: int
