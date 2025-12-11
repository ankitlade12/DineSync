"""
DineSync - Group Dining Consensus App

Solves the "Where should we eat?" problem with AI-powered group consensus.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dinesync.session_manager import SessionManager, Participant
from dinesync.consensus_engine import (
    ConsensusEngine,
    UserPreferences,
    Restaurant,
)
from dinesync.yelp_ai_client import YelpAIClient
from dinesync.yelp_fusion_client import YelpFusionClient, YelpFusionError
from dinesync.config import get_settings
import time
import re


# Page config
st.set_page_config(
    page_title="DineSync - Group Dining Consensus",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .session-link {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    .participant-card {
        background-color: #f8f9fa;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4ECDC4;
    }
    .satisfaction-meter {
        height: 30px;
        border-radius: 15px;
        background-color: #e0e0e0;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .satisfaction-fill {
        height: 100%;
        transition: width 0.3s ease;
    }
    .score-high { background-color: #4CAF50; }
    .score-medium { background-color: #FFC107; }
    .score-low { background-color: #FF5252; }
</style>
""", unsafe_allow_html=True)


# Initialize managers
@st.cache_resource
def get_session_manager():
    return SessionManager()

@st.cache_resource
def get_consensus_engine():
    return ConsensusEngine()

@st.cache_resource
def get_yelp_client():
    settings = get_settings()
    return YelpAIClient(settings.yelp_api_key)


def render_satisfaction_meter(score: float, name: str):
    """Render a visual satisfaction meter"""
    percentage = int(score * 100)
    
    if score >= 0.8:
        color_class = "score-high"
        emoji = "✅"
    elif score >= 0.6:
        color_class = "score-medium"
        emoji = "⚠️"
    else:
        color_class = "score-low"
        emoji = "❌"
    
    st.markdown(f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span><strong>{name}</strong></span>
            <span>{emoji} {percentage}%</span>
        </div>
        <div class="satisfaction-meter">
            <div class="satisfaction-fill {color_class}" style="width: {percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_session_page():
    """Page 1: Create a new dining session"""
    st.markdown('<div class="main-header">🍽️ DineSync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Solve the "Where should we eat?" problem with AI</div>', unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Create a Dine Session")
        st.write("Get your group together and find the perfect restaurant!")
        
        location = st.text_input(
            "📍 Where are you dining?",
            placeholder="e.g., Austin, TX or Downtown San Francisco",
            help="Enter a city, neighborhood, or address"
        )
        
        if st.button("🚀 Create Session", type="primary", use_container_width=True):
            if not location:
                st.error("Please enter a location!")
            else:
                session_manager = get_session_manager()
                session_id = session_manager.create_session(location)
                
                st.success("✅ Session created!")
                
                # Generate shareable link
                base_url = "http://localhost:8501"  # Update for production
                session_url = f"{base_url}/?session={session_id}"
                
                st.markdown(f"""
                <div class="session-link">
                    <strong>📎 Share this link with your group:</strong><br/>
                    <code>{session_url}</code>
                </div>
                """, unsafe_allow_html=True)
                
                st.code(session_url, language=None)
                
                st.info("👆 Copy this link and send it to your friends! Everyone can submit their preferences.")
                
                # Auto-redirect to join page
                time.sleep(2)
                st.query_params["session"] = session_id
                st.rerun()
    
    # How it works
    st.write("---")
    st.subheader("How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1️⃣ Create Session")
        st.write("Start a session and share the link with your group")
    
    with col2:
        st.markdown("### 2️⃣ Submit Preferences")
        st.write("Everyone inputs their cuisine, dietary needs, and budget")
    
    with col3:
        st.markdown("### 3️⃣ Find Consensus")
        st.write("AI finds restaurants that make everyone happy!")


def join_session_page(session_id: str):
    """Page 2: Join a session and submit preferences"""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        st.error("❌ Session not found!")
        if st.button("← Go Back"):
            st.query_params.clear()
            st.rerun()
        return
    
    st.markdown('<div class="main-header">🍽️ DineSync</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Dining in {session.location}</div>', unsafe_allow_html=True)
    
    # Sidebar: Show participants
    with st.sidebar:
        st.subheader("👥 Participants")
        st.write(f"**{len(session.participants)}** people joined")
        
        for participant in session.participants:
            st.markdown(f"""
            <div class="participant-card">
                <strong>{participant.name}</strong><br/>
                <small>✅ Preferences submitted</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Auto-refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        st.caption("Page refreshes automatically every 5 seconds")
    
    # Main content
    st.subheader("Submit Your Preferences")
    
    with st.form("preferences_form"):
        name = st.text_input(
            "Your Name",
            placeholder="e.g., Alice",
            help="How should we identify you?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            cuisines = st.multiselect(
                "🍕 Cuisine Preferences",
                options=[
                    "Italian", "Mexican", "Chinese", "Japanese", "Thai",
                    "Indian", "American", "French", "Mediterranean", "Korean",
                    "Vietnamese", "Greek", "Spanish", "Middle Eastern", "Any"
                ],
                help="Select all cuisines you'd enjoy"
            )
            
            dietary = st.multiselect(
                "🥗 Dietary Restrictions",
                options=[
                    "Vegetarian", "Vegan", "Gluten-free", "Dairy-free",
                    "Nut-free", "Halal", "Kosher", "None"
                ],
                help="Critical restrictions only (we enforce these strictly)"
            )
            
            budget = st.select_slider(
                "💰 Budget",
                options=["$", "$$", "$$$", "$$$$"],
                value="$$",
                help="$ = Under $15, $$ = $15-30, $$$ = $30-60, $$$$ = $60+"
            )
        
        with col2:
            max_distance = st.slider(
                "📍 Maximum Distance (miles)",
                min_value=0.5,
                max_value=10.0,
                value=3.0,
                step=0.5,
                help="How far are you willing to travel?"
            )
            
            ambiance = st.multiselect(
                "✨ Ambiance Preferences",
                options=[
                    "Casual", "Upscale", "Romantic", "Family-friendly",
                    "Trendy", "Cozy", "Lively", "Quiet", "Any"
                ],
                help="What vibe are you looking for?"
            )
            
            # NEW: Veto Power
            veto_items = st.multiselect(
                "🚫 Absolute Dealbreakers (Veto Power)",
                options=[
                    "Seafood", "Peanuts", "Shellfish", "Spicy food",
                    "Loud music", "Smoking area", "No parking"
                ],
                help="⚠️ These will COMPLETELY eliminate restaurants (use for severe allergies or strong dislikes)"
            )
        
        submitted = st.form_submit_button("✅ Submit My Preferences", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("Please enter your name!")
            elif not cuisines:
                st.error("Please select at least one cuisine!")
            else:
                # Add participant
                success = session_manager.add_participant(
                    session_id=session_id,
                    name=name,
                    cuisines=cuisines,
                    dietary_restrictions=[d for d in dietary if d != "None"],
                    budget=budget,
                    max_distance=max_distance,
                    ambiance=[a for a in ambiance if a != "Any"],
                    veto_items=veto_items  # NEW: Veto power
                )
                
                if success:
                    st.success(f"✅ Thanks {name}! Your preferences have been saved.")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to save preferences. Please try again.")
    
    # Check if we have enough participants to show results
    if len(session.participants) >= 2:
        st.write("---")
        st.info(f"🎉 {len(session.participants)} people have submitted! Ready to find restaurants?")
        
        if st.button("🔍 Find Restaurants", type="primary", use_container_width=True):
            st.query_params["session"] = session_id
            st.query_params["view"] = "results"
            st.rerun()
    
    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()


def generate_ai_explanation(result, user_prefs: List[UserPreferences]) -> str:
    """Generate AI explanation for why this restaurant is recommended"""
    restaurant = result.restaurant
    explanations = []
    
    # Find what it satisfies
    for prefs in user_prefs:
        score = result.individual_scores[prefs.name]
        if score > 0.8:
            if restaurant.cuisine in prefs.cuisines:
                explanations.append(f"✅ Satisfies {prefs.name}'s {restaurant.cuisine} preference")
            if all(d in restaurant.dietary_options for d in prefs.dietary_restrictions):
                dietary_str = ", ".join(prefs.dietary_restrictions)
                explanations.append(f"✅ Has {dietary_str} options for {prefs.name}")
            if restaurant.price == prefs.budget:
                explanations.append(f"✅ Matches {prefs.name}'s {prefs.budget} budget")
        elif score < 0.6:
            explanations.append(f"⚠️ {prefs.name} is compromising here")
    
    if not explanations:
        explanations.append("🤝 Fair compromise for everyone")
    
    return "\n".join(explanations)


def generate_detailed_ai_response(
    question: str, 
    restaurant: Restaurant, 
    individual_scores: dict,
    user_prefs: List[UserPreferences]
) -> str:
    """Generate detailed AI response based on the question asked"""
    
    question_lower = question.lower()
    
    # Analyze question intent and provide detailed response
    if any(word in question_lower for word in ["best", "recommend", "choose", "pick", "should"]):
        # Question about which is best
        response_parts = [
            f"**{restaurant.name}** is an excellent choice! Here's a detailed breakdown:",
            "",
            f"**🍽️ Cuisine & Quality**: This {restaurant.cuisine} restaurant has earned a {restaurant.rating}⭐ rating on Yelp. {restaurant.review_snippet}",
            "",
        ]
        
        # Add price context
        price_map = {"$": "Budget-friendly (under $15/person)", "$$": "Moderate ($15-30/person)", 
                     "$$$": "Upscale ($30-60/person)", "$$$$": "Fine dining ($60+/person)"}
        response_parts.append(f"**💰 Price Point**: {restaurant.price} - {price_map.get(restaurant.price, 'Moderate pricing')}")
        response_parts.append("")
        
        # Add location details
        response_parts.append(f"**📍 Location**: {restaurant.address} - Just {restaurant.distance} miles away (approximately {int(restaurant.distance * 3)}-{int(restaurant.distance * 4)} minute drive)")
        response_parts.append("")
        
        # Add ambiance
        response_parts.append(f"**✨ Ambiance**: {restaurant.ambiance} atmosphere, perfect for a comfortable dining experience")
        response_parts.append("")
        
        # Add dietary options
        if restaurant.dietary_options:
            dietary_str = ", ".join(restaurant.dietary_options)
            response_parts.append(f"**🥗 Dietary Options**: {dietary_str}")
            
            # Check which users' dietary needs are met
            satisfied_users = []
            for prefs in user_prefs:
                if all(d in restaurant.dietary_options for d in prefs.dietary_restrictions):
                    satisfied_users.append(prefs.name)
            
            if satisfied_users:
                response_parts.append(f"   ✅ Accommodates dietary needs for: {', '.join(satisfied_users)}")
            response_parts.append("")
        
        # Add recommendation
        response_parts.append(f"**👨‍🍳 Why This Restaurant**: With its {restaurant.rating}⭐ rating and {restaurant.ambiance.lower()} setting, {restaurant.name} offers a great dining experience. The restaurant is particularly known for {restaurant.review_snippet.lower()}")
        
        return "\n".join(response_parts)
    
    elif any(word in question_lower for word in ["outdoor", "seating", "patio", "outside"]):
        # Question about outdoor seating
        return f"Based on the {restaurant.ambiance.lower()} ambiance at **{restaurant.name}**, outdoor seating may be available. The restaurant is known for {restaurant.review_snippet.lower()} In production, I would check real-time Yelp data for confirmed outdoor seating availability."
    
    elif any(word in question_lower for word in ["vegetarian", "vegan", "dietary", "gluten", "allergen", "allergy"]):
        # Question about dietary options
        if restaurant.dietary_options:
            options_str = ", ".join(restaurant.dietary_options)
            response = f"**{restaurant.name}** offers the following dietary options: **{options_str}**.\n\n"
            
            # Check which users' dietary needs are met
            satisfied_users = []
            for prefs in user_prefs:
                if all(d in restaurant.dietary_options for d in prefs.dietary_restrictions):
                    satisfied_users.append(prefs.name)
            
            if satisfied_users:
                response += f"This satisfies the dietary requirements for: {', '.join(satisfied_users)}."
            
            return response
        else:
            return f"**{restaurant.name}** doesn't have specific dietary options listed, but you can call ahead to confirm accommodations."
    
    elif any(word in question_lower for word in ["price", "cost", "expensive", "cheap", "budget", "afford"]):
        # Question about pricing
        price_details = {
            "$": "very affordable (under $15 per person)",
            "$$": "moderately priced ($15-30 per person)",
            "$$$": "upscale pricing ($30-60 per person)",
            "$$$$": "fine dining pricing ($60+ per person)"
        }
        
        response = f"**{restaurant.name}** is rated **{restaurant.price}**, which means it's {price_details.get(restaurant.price, 'moderately priced')}.\n\n"
        
        # Check budget compatibility
        budget_match = []
        budget_compromise = []
        for prefs in user_prefs:
            if prefs.budget == restaurant.price:
                budget_match.append(prefs.name)
            else:
                budget_compromise.append(f"{prefs.name} (prefers {prefs.budget})")
        
        if budget_match:
            response += f"✅ Perfect budget match for: {', '.join(budget_match)}\n"
        if budget_compromise:
            response += f"⚠️ Slight budget difference for: {', '.join(budget_compromise)}"
        
        return response
    
    elif any(word in question_lower for word in ["distance", "far", "close", "location", "where", "drive"]):
        # Question about location/distance
        return f"**{restaurant.name}** is located at {restaurant.address}, approximately **{restaurant.distance} miles** away. That's about a {int(restaurant.distance * 3)}-{int(restaurant.distance * 4)} minute drive depending on traffic."
    
    elif any(word in question_lower for word in ["ambiance", "atmosphere", "vibe", "mood", "romantic", "casual", "fancy"]):
        # Question about ambiance
        response = f"**{restaurant.name}** has a **{restaurant.ambiance.lower()}** ambiance. {restaurant.review_snippet}\n\n"
        
        # Check ambiance preferences
        ambiance_match = []
        for prefs in user_prefs:
            if restaurant.ambiance in prefs.ambiance or not prefs.ambiance:
                ambiance_match.append(prefs.name)
        
        if ambiance_match:
            response += f"This matches the ambiance preferences of: {', '.join(ambiance_match)}"
        
        return response
    
    elif any(word in question_lower for word in ["rating", "review", "quality", "good"]):
        # Question about ratings/reviews
        return f"**{restaurant.name}** has a **{restaurant.rating}⭐** rating on Yelp. Customers say: \"{restaurant.review_snippet}\" This indicates {('excellent' if restaurant.rating >= 4.5 else 'very good' if restaurant.rating >= 4.0 else 'good')} quality and customer satisfaction."
    
    else:
        # General question - provide comprehensive overview
        return f"""**{restaurant.name}** - {restaurant.cuisine} Restaurant

**Overview**: {restaurant.review_snippet}

**Key Details**:
- Rating: {restaurant.rating}⭐
- Price: {restaurant.price}
- Distance: {restaurant.distance} miles
- Ambiance: {restaurant.ambiance}
- Dietary Options: {', '.join(restaurant.dietary_options) if restaurant.dietary_options else 'Standard menu'}

**Location**: {restaurant.address}

This restaurant has a group satisfaction score of {int(sum(individual_scores.values()) / len(individual_scores) * 100)}% for your group."""


def results_page(session_id: str):
    """Page 3: Show consensus results"""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        st.error("❌ Session not found!")
        return
    
    if len(session.participants) < 1:
        st.warning("⚠️ No participants yet! Share the session link to get started.")
        return
    
    st.markdown('<div class="main-header">🎯 Your Perfect Restaurants</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Based on {len(session.participants)} people\'s preferences</div>', unsafe_allow_html=True)
    
    # Convert participants to UserPreferences
    user_prefs = []
    for p in session.participants:
        user_prefs.append(UserPreferences(
            name=p.name,
            cuisines=p.cuisines,
            dietary_restrictions=p.dietary_restrictions,
            budget=p.budget,
            max_distance=p.max_distance,
            ambiance=p.ambiance,
            veto_items=p.veto_items if hasattr(p, 'veto_items') else []  # NEW: Veto power
        ))
    
    
    
    # Search for restaurants using Yelp Fusion API
    with st.spinner("🔍 Searching for real restaurants on Yelp..."):
        try:
            # Collect all cuisines and price ranges
            all_cuisines = set()
            all_prices = set()
            max_dist = 0
            
            for prefs in user_prefs:
                all_cuisines.update(prefs.cuisines)
                all_prices.add(prefs.budget)
                max_dist = max(max_dist, prefs.max_distance)
            
            # Remove "Any" from cuisines
            all_cuisines.discard("Any")
            
            # Convert distance from miles to meters
            radius_meters = int(max_dist * 1609.34)
            
            # Search using Yelp Fusion API
            fusion_client = YelpFusionClient()
            yelp_businesses = fusion_client.search_restaurants(
                location=session.location,
                cuisines=list(all_cuisines) if all_cuisines else None,
                price=list(all_prices) if all_prices else None,
                radius=radius_meters,
                limit=50  # Increased limit to get more diverse results
            )
            
            if not yelp_businesses:
                st.error("No restaurants found on Yelp. Try adjusting your search criteria.")
                return
            
            # Convert Yelp businesses to Restaurant objects
            restaurants = []
            for biz in yelp_businesses:
                # Extract cuisine from categories
                cuisine = "Various"
                if biz.get("categories"):
                    cuisine = biz["categories"][0].get("title", "Various")
                
                # Convert price level
                price = biz.get("price", "$$")
                
                # Calculate distance in miles
                distance = biz.get("distance", 0) / 1609.34  # meters to miles
                
                # Infer dietary options from categories and attributes
                dietary_options = []
                categories_str = " ".join([cat.get("alias", "") for cat in biz.get("categories", [])])
                name_and_cats = (biz.get("name", "") + " " + categories_str).lower()
                
                # Most modern restaurants offer vegetarian options
                # Assume Vegetarian is available unless it's explicitly a steakhouse/BBQ
                if not any(term in name_and_cats for term in ["steakhouse", "bbq", "barbecue", "smokehouse"]):
                    dietary_options.append("Vegetarian")
                
                # Check for vegan-friendly indicators
                # Many restaurants now offer vegan options, especially upscale ones
                if any(term in name_and_cats for term in ["vegan", "vegetarian", "plant", "salad", "mediterranean", "italian", "indian", "thai", "mexican"]):
                    if "Vegetarian" not in dietary_options:
                        dietary_options.append("Vegetarian")
                    dietary_options.append("Vegan")
                elif price in ["$$$", "$$$$"]:
                    # Upscale restaurants typically accommodate vegan requests
                    dietary_options.append("Vegan")
                
                # Check for gluten-free indicators
                if any(term in name_and_cats for term in ["gluten", "health", "salad", "mediterranean"]):
                    dietary_options.append("Gluten-free")
                
                # Most restaurants can accommodate nut allergies
                # Add Nut-free unless it's explicitly a nut-focused restaurant
                if not any(term in name_and_cats for term in ["peanut", "almond", "walnut", "pecan"]):
                    dietary_options.append("Nut-free")
                
                # Halal - Add to Middle Eastern, Indian, Pakistani, Mediterranean restaurants
                if any(term in name_and_cats for term in ["halal", "middle", "mediterranean", "turkish", "lebanese", "pakistani", "indian"]):
                    dietary_options.append("Halal")
                
                # Kosher - Add to Jewish delis and restaurants that typically offer kosher
                if any(term in name_and_cats for term in ["kosher", "jewish", "deli", "bagel"]):
                    dietary_options.append("Kosher")
                
                # Dairy-free - Most restaurants can accommodate, especially Asian cuisines
                if any(term in name_and_cats for term in ["vegan", "asian", "thai", "vietnamese", "chinese", "japanese"]):
                    dietary_options.append("Dairy-free")
                elif price in ["$$$", "$$$$"]:
                    # Upscale restaurants can accommodate dairy-free requests
                    dietary_options.append("Dairy-free")
                
                # Soy-free - Most non-Asian restaurants don't use soy heavily
                if not any(term in name_and_cats for term in ["asian", "chinese", "japanese", "korean", "sushi"]):
                    dietary_options.append("Soy-free")
                
                # Shellfish-free - Most restaurants except seafood places
                if not any(term in name_and_cats for term in ["seafood", "sushi", "oyster", "crab", "lobster"]):
                    dietary_options.append("Shellfish-free")
                
                # Infer ambiance from price and categories
                ambiance = "Casual"
                if price in ["$$$", "$$$$"]:
                    ambiance = "Upscale"
                elif "romantic" in categories_str.lower():
                    ambiance = "Romantic"
                elif "family" in categories_str.lower():
                    ambiance = "Family-friendly"
                
                # Get review snippet
                review_snippet = "Great food and service!"
                if biz.get("review_count", 0) > 0:
                    review_snippet = f"Rated {biz.get('rating', 4.0)}⭐ by {biz.get('review_count', 0)} reviewers"
                
                # Create Restaurant object
                restaurant = Restaurant(
                    name=biz.get("name", "Unknown"),
                    cuisine=cuisine,
                    price=price,
                    distance=round(distance, 1),
                    rating=biz.get("rating", 4.0),
                    dietary_options=dietary_options,
                    ambiance=ambiance,
                    address=biz.get("location", {}).get("display_address", [""])[0] or session.location,
                    review_snippet=review_snippet
                )
                restaurants.append(restaurant)
            
        except YelpFusionError as e:
            st.error(f"Error searching Yelp: {str(e)}")
            st.info("💡 For demo purposes, showing sample restaurants...")
            restaurants = get_sample_restaurants(user_prefs)
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.info("💡 For demo purposes, showing sample restaurants...")
            restaurants = get_sample_restaurants(user_prefs)
    
    # Score restaurants
    with st.spinner("🧮 Calculating group consensus..."):
        consensus_engine = get_consensus_engine()
        results = consensus_engine.rank_restaurants(restaurants, user_prefs)
    
    # Display results
    st.subheader(f"🏆 Top {min(10, len(results))} Restaurants")
    
    # Show overall group compromise level
    avg_compromise = sum(r.compromise_level for r in results[:3]) / min(3, len(results))
    if avg_compromise >= 0.7:
        st.success("🟢 Low compromise needed - everyone will be happy!")
    elif avg_compromise >= 0.5:
        st.warning("🟡 Moderate compromise - most people satisfied")
    else:
        st.error("🔴 High compromise needed - consider splitting into groups")
    
    st.write("---")
    
    for idx, result in enumerate(results[:10], 1):
        with st.expander(f"#{idx} {result.restaurant.name} - {int(result.group_score * 100)}% Group Satisfaction", expanded=(idx <= 3)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{result.restaurant.cuisine}** • {result.restaurant.price} • ⭐ {result.restaurant.rating}")
                st.write(f"📍 {result.restaurant.address} ({result.restaurant.distance:.1f} mi)")
                
                if result.restaurant.review_snippet:
                    st.caption(f"💬 \"{result.restaurant.review_snippet}\"")
                
                st.write("---")
                
                # NEW: AI Explanation
                st.write("**🤖 Why we recommend this:**")
                st.info(generate_ai_explanation(result, user_prefs))
            
            with col2:
                st.metric("Group Score", f"{int(result.group_score * 100)}%")
                st.metric("Compromise Level", f"{int(result.compromise_level * 100)}%")
            
            # Individual satisfaction meters
            st.write("**Individual Satisfaction:**")
            for name, score in result.individual_scores.items():
                render_satisfaction_meter(score, name)
            
            # NEW: AI Conversation Mode
            with st.expander("💬 Ask AI about this restaurant"):
                question = st.text_input(
                    "Ask a question",
                    placeholder="e.g., Does this place have outdoor seating?",
                    key=f"q_{idx}"
                )
                if st.button("Ask", key=f"ask_{idx}"):
                    if question:
                        # Generate detailed AI response
                        st.write(f"🤖 **AI Response:**")
                        ai_response = generate_detailed_ai_response(
                            question, 
                            result.restaurant, 
                            result.individual_scores,
                            user_prefs
                        )
                        st.write(ai_response)
                        st.caption("💡 In production, this would use Yelp AI's multi-turn conversation API")
            
            # Book reservation button (simulated)
            if st.button(f"📅 Book Reservation at {result.restaurant.name}", key=f"book_{idx}"):
                st.success(f"🎉 Reservation requested at {result.restaurant.name}!")
                st.info("💡 In production, this would use Yelp AI's reservation API")


def build_yelp_query(location: str, user_prefs: List[UserPreferences]) -> str:
    """Build a Yelp AI query combining all user preferences"""
    
    # Collect all cuisines
    all_cuisines = set()
    for prefs in user_prefs:
        all_cuisines.update(prefs.cuisines)
    
    # Collect all dietary restrictions
    all_dietary = set()
    for prefs in user_prefs:
        all_dietary.update(prefs.dietary_restrictions)
    
    # Get budget range
    budgets = [prefs.budget for prefs in user_prefs]
    min_budget = min(budgets, key=lambda b: ConsensusEngine.BUDGET_MAP.get(b, 2))
    max_budget = max(budgets, key=lambda b: ConsensusEngine.BUDGET_MAP.get(b, 2))
    
    # Get max distance
    max_dist = max(prefs.max_distance for prefs in user_prefs)
    
    # Build query
    query_parts = [f"Find restaurants in {location}"]
    
    if all_cuisines:
        cuisines_str = ", ".join(list(all_cuisines)[:5])
        query_parts.append(f"that serve {cuisines_str} food")
    
    if all_dietary:
        dietary_str = ", ".join(all_dietary)
        query_parts.append(f"with {dietary_str} options")
    
    if min_budget == max_budget:
        query_parts.append(f"in the {min_budget} price range")
    else:
        query_parts.append(f"in the {min_budget} to {max_budget} price range")
    
    query_parts.append(f"within {max_dist} miles")
    
    return " ".join(query_parts)


def parse_yelp_response(response: dict, user_prefs: List[UserPreferences] = None) -> List[Restaurant]:
    """Parse Yelp AI response into Restaurant objects"""
    
    try:
        # Extract text from Yelp AI response
        text = response.get("response", {}).get("text", "")
        
        if not text:
            # No response text, use sample data
            return get_sample_restaurants(user_prefs)
        
        # Try to extract restaurant information from the text
        # Yelp AI returns conversational text, not structured data
        # We'll look for patterns like restaurant names, ratings, etc.
        
        restaurants = []
        lines = text.split('\n')
        
        current_restaurant = {}
        for line in lines:
            line = line.strip()
            
            # Look for restaurant names (usually start with numbers or bullets)
            if any(line.startswith(str(i)) for i in range(1, 20)):
                # Save previous restaurant if exists
                if current_restaurant.get('name'):
                    try:
                        restaurants.append(Restaurant(
                            name=current_restaurant.get('name', 'Unknown'),
                            cuisine=current_restaurant.get('cuisine', 'Various'),
                            price=current_restaurant.get('price', '$$'),
                            distance=current_restaurant.get('distance', 2.0),
                            rating=current_restaurant.get('rating', 4.0),
                            dietary_options=current_restaurant.get('dietary_options', ['Vegetarian', 'Vegan']),
                            ambiance=current_restaurant.get('ambiance', 'Casual'),
                            address=current_restaurant.get('address', 'Dallas, TX'),
                            review_snippet=current_restaurant.get('review_snippet', 'Great food and service!')
                        ))
                    except Exception:
                        pass
                
                # Start new restaurant
                current_restaurant = {}
                # Extract name (remove number/bullet)
                name = line.split('.', 1)[-1].split('-', 1)[0].strip()
                current_restaurant['name'] = name
                
            # Look for price indicators
            if '$' in line:
                price_match = line.count('$')
                current_restaurant['price'] = '$' * min(price_match, 4)
            
            # Look for ratings
            if '⭐' in line or 'star' in line.lower():
                try:
                    # Extract rating number
                    import re
                    rating_match = re.search(r'(\d+\.?\d*)\s*(?:⭐|star)', line)
                    if rating_match:
                        current_restaurant['rating'] = float(rating_match.group(1))
                except Exception:
                    pass
        
        # Add last restaurant
        if current_restaurant.get('name'):
            try:
                restaurants.append(Restaurant(
                    name=current_restaurant.get('name', 'Unknown'),
                    cuisine=current_restaurant.get('cuisine', 'Various'),
                    price=current_restaurant.get('price', '$$'),
                    distance=current_restaurant.get('distance', 2.0),
                    rating=current_restaurant.get('rating', 4.0),
                    dietary_options=current_restaurant.get('dietary_options', ['Vegetarian', 'Vegan']),
                    ambiance=current_restaurant.get('ambiance', 'Casual'),
                    address=current_restaurant.get('address', 'Dallas, TX'),
                    review_snippet=current_restaurant.get('review_snippet', 'Great food and service!')
                ))
            except Exception:
                pass
        
        # If we successfully parsed restaurants, return them
        if restaurants:
            return restaurants
        
    except Exception as e:
        # Parsing failed, fall back to sample data
        print(f"Error parsing Yelp response: {e}")
    
    # Fall back to sample data based on user preferences
    return get_sample_restaurants(user_prefs)


def get_sample_restaurants(user_prefs: List[UserPreferences] = None) -> List[Restaurant]:
    """Generate sample restaurants based on user preferences"""
    
    # Collect all unique cuisines from user preferences
    if user_prefs:
        all_cuisines = set()
        for prefs in user_prefs:
            all_cuisines.update(prefs.cuisines)
        # Remove "Any" if present
        all_cuisines.discard("Any")
    else:
        # Default cuisines if no preferences provided
        all_cuisines = {"Italian", "Mexican", "Japanese"}
    
    # Restaurant templates for different cuisines
    restaurant_templates = {
        "Italian": {
            "name": "Trattoria Bella",
            "price": "$$",
            "distance": 1.2,
            "rating": 4.5,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Romantic",
            "review_snippet": "Amazing pasta and great atmosphere!"
        },
        "Mexican": {
            "name": "Taco Fiesta",
            "price": "$",
            "distance": 0.8,
            "rating": 4.3,
            "dietary_options": ["Vegetarian", "Vegan"],
            "ambiance": "Casual",
            "review_snippet": "Best tacos in town, super affordable!"
        },
        "Japanese": {
            "name": "Sushi Palace",
            "price": "$$$",
            "distance": 2.1,
            "rating": 4.7,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Upscale",
            "review_snippet": "Fresh fish and elegant presentation"
        },
        "Indian": {
            "name": "Spice Garden",
            "price": "$$",
            "distance": 1.5,
            "rating": 4.6,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Casual",
            "review_snippet": "Authentic flavors and generous portions!"
        },
        "Chinese": {
            "name": "Golden Dragon",
            "price": "$$",
            "distance": 1.8,
            "rating": 4.4,
            "dietary_options": ["Vegetarian", "Vegan"],
            "ambiance": "Family-friendly",
            "review_snippet": "Delicious dim sum and friendly service"
        },
        "Thai": {
            "name": "Bangkok Bistro",
            "price": "$$",
            "distance": 2.0,
            "rating": 4.5,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Cozy",
            "review_snippet": "Perfect balance of flavors, love the curry!"
        },
        "American": {
            "name": "The Burger Joint",
            "price": "$",
            "distance": 0.5,
            "rating": 4.2,
            "dietary_options": ["Vegetarian", "Vegan"],
            "ambiance": "Casual",
            "review_snippet": "Classic American comfort food done right"
        },
        "French": {
            "name": "Le Petit Bistro",
            "price": "$$$$",
            "distance": 2.5,
            "rating": 4.8,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Romantic",
            "review_snippet": "Exquisite French cuisine, worth every penny"
        },
        "Mediterranean": {
            "name": "Olive Grove",
            "price": "$$",
            "distance": 1.3,
            "rating": 4.5,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Casual",
            "review_snippet": "Fresh ingredients and healthy options"
        },
        "Korean": {
            "name": "Seoul Kitchen",
            "price": "$$",
            "distance": 1.9,
            "rating": 4.6,
            "dietary_options": ["Vegetarian", "Vegan"],
            "ambiance": "Trendy",
            "review_snippet": "Amazing BBQ and banchan selection"
        },
        "Vietnamese": {
            "name": "Pho Paradise",
            "price": "$",
            "distance": 1.1,
            "rating": 4.4,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Casual",
            "review_snippet": "Best pho in town, fresh and flavorful"
        },
        "Greek": {
            "name": "Athena's Table",
            "price": "$$",
            "distance": 1.7,
            "rating": 4.5,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Family-friendly",
            "review_snippet": "Authentic Greek food with great atmosphere"
        },
        "Spanish": {
            "name": "Tapas Bar",
            "price": "$$$",
            "distance": 2.2,
            "rating": 4.7,
            "dietary_options": ["Vegetarian", "Vegan", "Gluten-free"],
            "ambiance": "Lively",
            "review_snippet": "Amazing tapas and sangria selection"
        },
        "Middle Eastern": {
            "name": "Cedar Grill",
            "price": "$$",
            "distance": 1.4,
            "rating": 4.5,
            "dietary_options": ["Vegetarian", "Vegan", "Halal"],
            "ambiance": "Casual",
            "review_snippet": "Delicious shawarma and fresh hummus"
        }
    }
    
    # Generate restaurants for selected cuisines
    restaurants = []
    location = "Dallas, TX"  # Default location
    
    # Generate 2-3 variations per cuisine to ensure we have at least 5 restaurants
    for cuisine in all_cuisines:
        if cuisine in restaurant_templates:
            template = restaurant_templates[cuisine]
            
            # Variation 1: Original template
            restaurants.append(Restaurant(
                name=template["name"],
                cuisine=cuisine,
                price=template["price"],
                distance=template["distance"],
                rating=template["rating"],
                dietary_options=template["dietary_options"],
                ambiance=template["ambiance"],
                address=f"{template['name']}, {location}",
                review_snippet=template["review_snippet"]
            ))
            
            # Variation 2: Different price point and distance
            price_variations = {"$": "$$", "$$": "$$$", "$$$": "$$", "$$$$": "$$$"}
            alt_price = price_variations.get(template["price"], "$$")
            
            restaurants.append(Restaurant(
                name=f"{template['name']} Downtown",
                cuisine=cuisine,
                price=alt_price,
                distance=template["distance"] + 1.5,
                rating=max(3.8, template["rating"] - 0.3),
                dietary_options=template["dietary_options"],
                ambiance=template["ambiance"],
                address=f"{template['name']} Downtown, {location}",
                review_snippet=f"Great {cuisine.lower()} food with a modern twist!"
            ))
            
            # Variation 3: Budget-friendly option
            if len(restaurants) < 5:  # Only add third variation if we need more restaurants
                restaurants.append(Restaurant(
                    name=f"{cuisine} Express" if cuisine != "Italian" else "Pasta House",
                    cuisine=cuisine,
                    price="$" if template["price"] != "$" else "$$",
                    distance=template["distance"] + 0.5,
                    rating=max(3.5, template["rating"] - 0.5),
                    dietary_options=template["dietary_options"][:1] if template["dietary_options"] else [],
                    ambiance="Casual",
                    address=f"{cuisine} Express, {location}",
                    review_snippet=f"Quick and tasty {cuisine.lower()} cuisine at great prices!"
                ))
    
    # If no restaurants generated, return a default set
    if not restaurants:
        for cuisine in ["Italian", "Mexican", "Japanese"]:
            template = restaurant_templates[cuisine]
            restaurants.append(Restaurant(
                name=template["name"],
                cuisine=cuisine,
                price=template["price"],
                distance=template["distance"],
                rating=template["rating"],
                dietary_options=template["dietary_options"],
                ambiance=template["ambiance"],
                address=f"{template['name']}, {location}",
                review_snippet=template["review_snippet"]
            ))
    
    return restaurants


def main():
    """Main app router"""
    
    # Check for session parameter
    session_id = st.query_params.get("session")
    view = st.query_params.get("view")
    
    if session_id:
        if view == "results":
            results_page(session_id)
        else:
            join_session_page(session_id)
    else:
        create_session_page()


if __name__ == "__main__":
    main()
