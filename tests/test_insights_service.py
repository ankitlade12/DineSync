"""Tests for insights service."""

import pytest
from unittest.mock import Mock, patch

from yelpreviewgym.insights_service import (
    build_insights_prompt,
    parse_insights_json,
    build_scenarios_prompt,
    parse_scenarios_json,
    analyze_business,
    generate_scenarios,
    evaluate_staff_reply,
)
from yelpreviewgym.schemas import BusinessInsights, DialogueTurn, TrainingScenario


class TestPromptBuilders:
    """Test prompt generation functions."""
    
    def test_build_insights_prompt(self):
        """Test insights prompt generation."""
        prompt = build_insights_prompt("Joe's Pizza", "San Francisco, CA", "Restaurant")
        
        assert "Joe's Pizza" in prompt
        assert "San Francisco, CA" in prompt
        assert "Restaurant" in prompt
        assert "delights" in prompt
        assert "pains" in prompt
        assert "personas" in prompt
    
    def test_build_scenarios_prompt_with_pains(self):
        """Test scenarios prompt with pain points."""
        pains = ["Long wait times", "Cold food", "Rude staff"]
        prompt = build_scenarios_prompt("Joe's Pizza", "San Francisco", "Restaurant", pains)
        
        assert "Joe's Pizza" in prompt
        assert "Long wait times" in prompt
        assert "Cold food" in prompt
        # Only top 2 pains should be included
        assert prompt.count("-") >= 2
    
    def test_build_scenarios_prompt_no_pains(self):
        """Test scenarios prompt without pain points."""
        prompt = build_scenarios_prompt("Joe's Pizza", "San Francisco", "Restaurant", [])
        
        assert "Joe's Pizza" in prompt
        assert "Customer service issues" in prompt


class TestJSONParsers:
    """Test JSON parsing functions."""
    
    def test_parse_insights_json_complete(self):
        """Test parsing complete insights JSON."""
        data = {
            "delights": ["Great pizza", "Fast service"],
            "pains": ["Noisy", "Limited parking"],
            "personas": ["Families", "Students"]
        }
        
        insights = parse_insights_json(data)
        
        assert isinstance(insights, BusinessInsights)
        assert len(insights.delights) == 2
        assert len(insights.pains) == 2
        assert len(insights.personas) == 2
        assert insights.delights[0] == "Great pizza"
    
    def test_parse_insights_json_empty_fields(self):
        """Test parsing insights with empty fields."""
        data = {
            "delights": [],
            "pains": ["Slow service"],
            "personas": []
        }
        
        insights = parse_insights_json(data)
        
        assert insights.delights == []
        assert len(insights.pains) == 1
        assert insights.personas == []
    
    def test_parse_insights_json_missing_fields(self):
        """Test parsing insights with missing fields."""
        data = {}
        
        insights = parse_insights_json(data)
        
        assert insights.delights == []
        assert insights.pains == []
        assert insights.personas == []
    
    def test_parse_scenarios_json_complete(self):
        """Test parsing complete scenarios JSON."""
        data = {
            "scenarios": [
                {
                    "title": "Cold Food Complaint",
                    "pain_summary": "Customer received cold food",
                    "bad_dialogue": [
                        {"speaker": "Customer", "text": "My food is cold!"},
                        {"speaker": "Staff", "text": "Not my problem."}
                    ],
                    "good_dialogue": [
                        {"speaker": "Customer", "text": "My food is cold!"},
                        {"speaker": "Staff", "text": "I'm so sorry! Let me fix that."}
                    ]
                }
            ]
        }
        
        scenarios = parse_scenarios_json(data)
        
        assert len(scenarios) == 1
        assert isinstance(scenarios[0], TrainingScenario)
        assert scenarios[0].title == "Cold Food Complaint"
        assert len(scenarios[0].bad_dialogue) == 2
        assert len(scenarios[0].good_dialogue) == 2
    
    def test_parse_scenarios_json_empty(self):
        """Test parsing empty scenarios JSON."""
        data = {"scenarios": []}
        
        scenarios = parse_scenarios_json(data)
        
        assert scenarios == []
    
    def test_parse_scenarios_json_malformed(self):
        """Test parsing malformed scenarios."""
        data = {
            "scenarios": [
                {
                    "title": "Test Scenario",
                    # Missing required fields
                }
            ]
        }
        
        scenarios = parse_scenarios_json(data)
        
        assert len(scenarios) == 1
        assert scenarios[0].title == "Test Scenario"
        assert scenarios[0].pain_summary == ""


class TestServiceFunctions:
    """Test main service functions."""
    
    @patch('yelpreviewgym.insights_service.YelpAIClient')
    def test_analyze_business_success(self, mock_client_class):
        """Test successful business analysis."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock API response
        mock_response = {
            "response": {
                "text": '{"delights": ["Great food"], "pains": ["Slow service"], "personas": ["Foodies"]}'
            }
        }
        mock_client.chat.return_value = mock_response
        
        # Mock the static method
        mock_client_class.json_from_response.return_value = (
            {"delights": ["Great food"], "pains": ["Slow service"], "personas": ["Foodies"]},
            '{"delights": ["Great food"], "pains": ["Slow service"], "personas": ["Foodies"]}'
        )
        
        insights, raw = analyze_business("Joe's Pizza", "San Francisco", "Restaurant")
        
        assert insights is not None
        assert len(insights.delights) == 1
        assert insights.delights[0] == "Great food"
        assert "Great food" in raw
    
    @patch('yelpreviewgym.insights_service.YelpAIClient')
    def test_analyze_business_api_error(self, mock_client_class):
        """Test business analysis with API error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("API Error")
        
        insights, raw = analyze_business("Joe's Pizza", "San Francisco", "Restaurant")
        
        # Should return None on error
        assert insights is None
        assert raw == ""
    
    @patch('yelpreviewgym.insights_service.YelpAIClient')
    def test_generate_scenarios_success(self, mock_client_class):
        """Test successful scenario generation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = {
            "response": {
                "text": '''{"scenarios": [{
                    "title": "Wait Time Complaint",
                    "pain_summary": "Long wait",
                    "bad_dialogue": [{"speaker": "Customer", "text": "This is taking forever!"}],
                    "good_dialogue": [{"speaker": "Customer", "text": "This is taking forever!"}]
                }]}'''
            }
        }
        mock_client.chat.return_value = mock_response
        
        # Mock the static method
        mock_client_class.json_from_response.return_value = (
            {"scenarios": [{
                "title": "Wait Time Complaint",
                "pain_summary": "Long wait",
                "bad_dialogue": [{"speaker": "Customer", "text": "This is taking forever!"}],
                "good_dialogue": [{"speaker": "Customer", "text": "This is taking forever!"}]
            }]},
            "raw_text"
        )
        
        pains = ["Long wait times"]
        scenarios, _ = generate_scenarios("Joe's Pizza", "SF", "Restaurant", pains)
        
        assert len(scenarios) >= 1
        assert isinstance(scenarios[0], TrainingScenario)
        assert scenarios[0].title == "Wait Time Complaint"
    
    @patch('yelpreviewgym.insights_service.YelpAIClient')
    def test_evaluate_staff_reply_success(self, mock_client_class):
        """Test successful staff reply evaluation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = {
            "response": {
                "text": '''{"score": 8.5, "summary": "Good response", 
                          "strengths": ["Empathetic"], 
                          "improvements": ["More specific"]}'''
            }
        }
        mock_client.chat.return_value = mock_response
        
        # Mock the static method
        mock_client_class.json_from_response.return_value = (
            {"score": 8.5, "summary": "Good response", 
             "strengths": ["Empathetic"], 
             "improvements": ["More specific"]},
            "raw_text"
        )
        
        scenario = TrainingScenario(
            title="Test",
            pain_summary="Test issue",
            bad_dialogue=[],
            good_dialogue=[]
        )
        
        feedback, _ = evaluate_staff_reply(
            "Joe's Pizza", "SF", "Restaurant", scenario, "I apologize for the inconvenience"
        )
        
        assert feedback is not None
        assert feedback.score == 8.5
        assert feedback.summary == "Good response"
