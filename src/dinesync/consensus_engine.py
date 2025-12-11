"""Consensus Engine for DineSync

Implements the group consensus algorithm that finds restaurants
satisfying multiple users with different preferences.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class UserPreferences:
    """Individual user's dining preferences"""
    name: str
    cuisines: List[str]
    dietary_restrictions: List[str]
    budget: str  # "$", "$$", "$$$", "$$$$"
    max_distance: float  # in miles
    ambiance: List[str]
    veto_items: List[str] = None  # NEW: Absolute dealbreakers


@dataclass
class Restaurant:
    """Restaurant data from Yelp AI"""
    name: str
    cuisine: str
    price: str
    distance: float
    rating: float
    dietary_options: List[str]
    ambiance: str
    address: str
    review_snippet: Optional[str] = None


@dataclass
class ConsensusResult:
    """Scored restaurant with individual and group scores"""
    restaurant: Restaurant
    group_score: float
    individual_scores: Dict[str, float]
    compromise_level: float
    explanation: str


class ConsensusEngine:
    """
    Calculates group consensus for restaurant selection.
    
    Algorithm:
    - Individual score: 0-100 based on preference matching
    - Group score: 70% average + 30% minimum (fairness weight)
    - Dietary restrictions are HARD requirements (violation = 0)
    """
    
    # Scoring weights (total = 100)
    CUISINE_WEIGHT = 30
    DIETARY_WEIGHT = 25  # All-or-nothing
    PRICE_WEIGHT = 20
    DISTANCE_WEIGHT = 15
    AMBIANCE_WEIGHT = 10
    
    # Budget mapping
    BUDGET_MAP = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
    
    def calculate_individual_score(
        self, 
        restaurant: Restaurant, 
        user_prefs: UserPreferences
    ) -> float:
        """
        Calculate how well a restaurant matches one user's preferences.
        Returns 0.0 - 1.0
        """
        score = 0.0
        
        # 0. VETO POWER (NEW) - Absolute dealbreakers
        if user_prefs.veto_items:
            # Check if restaurant has any vetoed items
            # For demo, we'll check against restaurant name/cuisine
            restaurant_text = f"{restaurant.name} {restaurant.cuisine}".lower()
            for veto in user_prefs.veto_items:
                if veto.lower() in restaurant_text:
                    # Critical veto - return 0 immediately
                    return 0.0
        
        
        # 1. DIETARY RESTRICTIONS (25 points) - HARD REQUIREMENT
        if user_prefs.dietary_restrictions:
            # Check if ALL dietary restrictions are met
            restaurant_options = [opt.lower() for opt in restaurant.dietary_options]
            for restriction in user_prefs.dietary_restrictions:
                if restriction.lower() not in restaurant_options:
                    # Critical failure - return 0 immediately
                    return 0.0
            score += self.DIETARY_WEIGHT
        else:
            # No restrictions = full points
            score += self.DIETARY_WEIGHT
        
        # 2. CUISINE MATCH (30 points)
        if user_prefs.cuisines:
            cuisine_lower = restaurant.cuisine.lower()
            user_cuisines_lower = [c.lower() for c in user_prefs.cuisines]
            
            if cuisine_lower in user_cuisines_lower:
                score += self.CUISINE_WEIGHT  # Perfect match
            elif any(uc in cuisine_lower or cuisine_lower in uc for uc in user_cuisines_lower):
                score += self.CUISINE_WEIGHT * 0.5  # Partial match
        else:
            # No preference = neutral
            score += self.CUISINE_WEIGHT * 0.5
        
        # 3. PRICE MATCH (20 points)
        if user_prefs.budget and restaurant.price:
            user_budget_val = self.BUDGET_MAP.get(user_prefs.budget, 2)
            restaurant_price_val = self.BUDGET_MAP.get(restaurant.price, 2)
            
            price_diff = abs(user_budget_val - restaurant_price_val)
            if price_diff == 0:
                score += self.PRICE_WEIGHT  # Exact match
            elif price_diff == 1:
                score += self.PRICE_WEIGHT * 0.5  # One level off
            # else: 0 points (too expensive or too cheap)
        else:
            score += self.PRICE_WEIGHT * 0.5
        
        # 4. DISTANCE (15 points)
        if restaurant.distance <= user_prefs.max_distance:
            # Closer is better
            distance_ratio = 1 - (restaurant.distance / user_prefs.max_distance)
            score += self.DISTANCE_WEIGHT * distance_ratio
        # else: 0 points (too far)
        
        # 5. AMBIANCE (10 points)
        if user_prefs.ambiance and restaurant.ambiance:
            ambiance_lower = restaurant.ambiance.lower()
            user_ambiance_lower = [a.lower() for a in user_prefs.ambiance]
            
            if ambiance_lower in user_ambiance_lower:
                score += self.AMBIANCE_WEIGHT
            elif any(ua in ambiance_lower or ambiance_lower in ua for ua in user_ambiance_lower):
                score += self.AMBIANCE_WEIGHT * 0.5
        else:
            score += self.AMBIANCE_WEIGHT * 0.5
        
        # Normalize to 0-1
        return score / 100.0
    
    def calculate_group_score(
        self,
        restaurant: Restaurant,
        all_user_prefs: List[UserPreferences]
    ) -> ConsensusResult:
        """
        Calculate group consensus score for a restaurant.
        
        Returns ConsensusResult with:
        - group_score: Weighted average (70% avg + 30% min)
        - individual_scores: Dict of {name: score}
        - compromise_level: Minimum individual score
        - explanation: Why this score
        """
        individual_scores = {}
        
        for user_prefs in all_user_prefs:
            score = self.calculate_individual_score(restaurant, user_prefs)
            individual_scores[user_prefs.name] = score
        
        if not individual_scores:
            return ConsensusResult(
                restaurant=restaurant,
                group_score=0.0,
                individual_scores={},
                compromise_level=0.0,
                explanation="No users to score"
            )
        
        # Calculate metrics
        scores_list = list(individual_scores.values())
        avg_score = sum(scores_list) / len(scores_list)
        min_score = min(scores_list)
        max_score = max(scores_list)
        
        # Group score: 70% average satisfaction + 30% fairness
        group_score = (avg_score * 0.7) + (min_score * 0.3)
        
        # Generate explanation
        explanation = self._generate_explanation(
            individual_scores, avg_score, min_score, max_score
        )
        
        return ConsensusResult(
            restaurant=restaurant,
            group_score=group_score,
            individual_scores=individual_scores,
            compromise_level=min_score,
            explanation=explanation
        )
    
    def _generate_explanation(
        self,
        individual_scores: Dict[str, float],
        avg_score: float,
        min_score: float,
        max_score: float
    ) -> str:
        """Generate human-readable explanation of the score"""
        
        # Find who's compromising
        compromiser = None
        for name, score in individual_scores.items():
            if score == min_score:
                compromiser = name
                break
        
        if max_score - min_score < 0.1:
            return "Everyone loves this option equally! 🎉"
        elif min_score < 0.5:
            return f"⚠️ {compromiser} is making a big compromise here"
        elif min_score < 0.7:
            return f"Fair compromise - {compromiser} is least satisfied but still okay"
        else:
            return "Great option for everyone! ✅"
    
    def rank_restaurants(
        self,
        restaurants: List[Restaurant],
        all_user_prefs: List[UserPreferences]
    ) -> List[ConsensusResult]:
        """
        Score and rank all restaurants by group consensus.
        Returns sorted list (best first)
        """
        results = []
        
        for restaurant in restaurants:
            result = self.calculate_group_score(restaurant, all_user_prefs)
            results.append(result)
        
        # Sort by group score (descending)
        results.sort(key=lambda r: r.group_score, reverse=True)
        
        return results
