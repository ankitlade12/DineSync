"""Tests for Yelp AI API client."""

import pytest
from unittest.mock import Mock, patch
import json

from yelpreviewgym.yelp_ai_client import YelpAIClient, YelpAIError


class TestYelpAIClient:
    """Test YelpAIClient functionality."""
    
    def test_client_initialization(self):
        """Test client initialization with API key."""
        client = YelpAIClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"
    
    def test_client_initialization_from_settings(self):
        """Test client initialization from settings."""
        with patch('yelpreviewgym.yelp_ai_client.get_settings') as mock_settings:
            mock_settings.return_value.yelp_api_key = "settings_key"
            client = YelpAIClient()
            assert client.api_key == "settings_key"
    
    @patch('yelpreviewgym.yelp_ai_client.requests.post')
    def test_chat_success(self, mock_post):
        """Test successful chat request."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "response": {"text": "Test response"},
            "chat_id": "chat_123"
        }
        mock_post.return_value = mock_response
        
        client = YelpAIClient(api_key="test_key")
        result = client.chat("Test query")
        
        assert result["response"]["text"] == "Test response"
        assert result["chat_id"] == "chat_123"
        mock_post.assert_called_once()
    
    @patch('yelpreviewgym.yelp_ai_client.requests.post')
    def test_chat_with_chat_id(self, mock_post):
        """Test chat request with existing chat_id."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"response": {"text": "Continued conversation"}}
        mock_post.return_value = mock_response
        
        client = YelpAIClient(api_key="test_key")
        result = client.chat("Follow-up query", chat_id="existing_chat_123")
        
        # Check that chat_id was included in request
        call_args = mock_post.call_args
        assert call_args[1]['json']['chat_id'] == "existing_chat_123"
    
    @patch('yelpreviewgym.yelp_ai_client.requests.post')
    def test_chat_api_error(self, mock_post):
        """Test handling of API error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API key"
        mock_post.return_value = mock_response
        
        client = YelpAIClient(api_key="invalid_key")
        
        with pytest.raises(YelpAIError) as exc_info:
            client.chat("Test query")
        
        assert "401" in str(exc_info.value)
        assert "Unauthorized" in str(exc_info.value)
    
    @patch('yelpreviewgym.yelp_ai_client.requests.post')
    def test_chat_json_parse_error(self, mock_post):
        """Test handling of JSON parse error."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        client = YelpAIClient(api_key="test_key")
        
        with pytest.raises(YelpAIError) as exc_info:
            client.chat("Test query")
        
        assert "Failed to parse" in str(exc_info.value)
    
    def test_extract_json_block_success(self):
        """Test extracting JSON block from text."""
        text = 'Some text before {"key": "value", "number": 42} some text after'
        result = YelpAIClient._extract_json_block(text)
        
        assert result == '{"key": "value", "number": 42}'
    
    def test_extract_json_block_no_json(self):
        """Test extracting JSON when none exists."""
        text = "Just plain text without any JSON"
        result = YelpAIClient._extract_json_block(text)
        
        assert result is None
    
    def test_extract_json_block_malformed(self):
        """Test extracting malformed JSON."""
        text = "Text with { but no closing brace"
        result = YelpAIClient._extract_json_block(text)
        
        assert result is None
    
    def test_json_from_response_success(self):
        """Test parsing JSON from API response."""
        raw = {
            "response": {
                "text": 'Here is the data: {"delights": ["good food"], "pains": ["slow service"]}'
            }
        }
        
        parsed, text = YelpAIClient.json_from_response(raw)
        
        assert parsed is not None
        assert parsed["delights"] == ["good food"]
        assert parsed["pains"] == ["slow service"]
        assert "Here is the data" in text
    
    def test_json_from_response_no_json(self):
        """Test parsing response with no JSON."""
        raw = {
            "response": {
                "text": "Just plain text response without JSON"
            }
        }
        
        parsed, text = YelpAIClient.json_from_response(raw)
        
        assert parsed is None
        assert text == "Just plain text response without JSON"
    
    def test_json_from_response_invalid_json(self):
        """Test parsing response with invalid JSON."""
        raw = {
            "response": {
                "text": "Data: {invalid json structure}"
            }
        }
        
        parsed, text = YelpAIClient.json_from_response(raw)
        
        assert parsed is None
        assert "invalid json structure" in text
    
    def test_json_from_response_empty(self):
        """Test parsing empty response."""
        raw = {}
        
        parsed, text = YelpAIClient.json_from_response(raw)
        
        assert parsed is None
        assert text == ""
