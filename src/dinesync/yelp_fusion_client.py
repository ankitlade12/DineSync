"""Yelp Fusion API Client

Handles communication with Yelp Fusion API for restaurant search.
Returns structured restaurant data instead of conversational text.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .config import get_settings


YELP_FUSION_URL = "https://api.yelp.com/v3/businesses/search"


class YelpFusionError(Exception):
    """Exception raised for Yelp Fusion API errors."""


class YelpFusionClient:
    """Client for interacting with Yelp Fusion API."""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.yelp_api_key
    
    def search_restaurants(
        self,
        location: str,
        cuisines: List[str] = None,
        price: List[str] = None,
        radius: float = 8000,  # meters (about 5 miles)
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants using Yelp Fusion API.
        
        Args:
            location: City, address, or neighborhood
            cuisines: List of cuisine types (e.g., ["italian", "mexican"])
            price: List of price levels (1=$, 2=$$, 3=$$$, 4=$$$$)
            radius: Search radius in meters (max 40000)
            limit: Number of results (max 50)
            
        Returns:
            List of restaurant dictionaries with structured data
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        
        params: Dict[str, Any] = {
            "location": location,
            "categories": "restaurants",
            "limit": min(limit, 50),
            "radius": min(int(radius), 40000),
        }
        
        # Add cuisine categories
        if cuisines:
            # Map common cuisine names to Yelp categories
            cuisine_map = {
                "italian": "italian",
                "mexican": "mexican",
                "chinese": "chinese",
                "japanese": "japanese",
                "thai": "thai",
                "indian": "indpak",
                "american": "newamerican",
                "french": "french",
                "mediterranean": "mediterranean",
                "korean": "korean",
                "vietnamese": "vietnamese",
                "greek": "greek",
                "spanish": "spanish",
                "middle eastern": "mideastern",
            }
            
            yelp_categories = []
            for cuisine in cuisines:
                cuisine_lower = cuisine.lower()
                if cuisine_lower in cuisine_map:
                    yelp_categories.append(cuisine_map[cuisine_lower])
            
            if yelp_categories:
                params["categories"] = ",".join(yelp_categories)
        
        # Add price filter
        if price:
            # Convert price strings to numbers
            price_nums = []
            for p in price:
                price_nums.append(str(len(p)))  # $ = 1, $$ = 2, etc.
            params["price"] = ",".join(price_nums)
        
        try:
            response = requests.get(
                YELP_FUSION_URL,
                headers=headers,
                params=params,
                timeout=30,
            )
            
            if not response.ok:
                raise YelpFusionError(
                    f"Yelp Fusion API error {response.status_code}: {response.text[:400]}"
                )
            
            data = response.json()
            return data.get("businesses", [])
            
        except requests.exceptions.RequestException as e:
            raise YelpFusionError(f"Request failed: {e}") from e
    
    def get_business_details(self, business_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific business.
        
        Args:
            business_id: Yelp business ID
            
        Returns:
            Business details dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        
        url = f"https://api.yelp.com/v3/businesses/{business_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if not response.ok:
                raise YelpFusionError(
                    f"Yelp Fusion API error {response.status_code}: {response.text[:400]}"
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise YelpFusionError(f"Request failed: {e}") from e
