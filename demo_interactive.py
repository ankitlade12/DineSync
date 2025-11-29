"""
YelpReviewGym Interactive Demo Script

This script demonstrates YelpReviewGym features including:
- Core workflow (analyze, generate, practice)
- Enhanced features (progress tracking, badges, difficulty levels)
- Perfect for presentations and demos!
"""

import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from yelpreviewgym.insights_service import (
    analyze_business,
    generate_scenarios,
    evaluate_staff_reply,
)
from yelpreviewgym.enhanced_features import (
    ProgressTracker,
    calculate_difficulty,
    award_badges_for_score,
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_step_1():
    """Demo: Analyze a business from Yelp reviews."""
    print_section("STEP 1: ANALYZE BUSINESS REVIEWS 📊")
    
    # Example business
    business_name = "Gary Danko"
    location = "San Francisco, CA"
    business_type = "Restaurant"
    
    print(f"🏢 Business: {business_name}")
    print(f"📍 Location: {location}")
    print(f"🍽️  Type: {business_type}\n")
    
    print("🔍 Analyzing Yelp reviews...")
    insights, raw = analyze_business(business_name, location, business_type)
    
    if insights:
        print("✅ Analysis complete!\n")
        
        print("🌟 DELIGHTS (What customers love):")
        for i, delight in enumerate(insights.delights, 1):
            print(f"   {i}. {delight}")
        
        print("\n😰 PAIN POINTS (What customers complain about):")
        for i, pain in enumerate(insights.pains, 1):
            print(f"   {i}. {pain}")
        
        print("\n👥 CUSTOMER PERSONAS:")
        for i, persona in enumerate(insights.personas, 1):
            print(f"   {i}. {persona}")
        
        return insights
    else:
        print("❌ Failed to analyze business")
        print(f"Raw response: {raw}")
        return None


def demo_step_2(insights):
    """Demo: Generate training scenarios from pain points."""
    print_section("STEP 2: GENERATE TRAINING SCENARIOS 🎭")
    
    if not insights or not insights.pains:
        print("⚠️  No pain points to work with. Skipping scenario generation.")
        return []
    
    business_name = "Gary Danko"
    location = "San Francisco, CA"
    business_type = "Restaurant"
    
    print(f"📝 Creating training scenarios based on {len(insights.pains)} pain points...\n")
    
    scenarios, raw = generate_scenarios(
        business_name, location, business_type, insights.pains
    )
    
    if scenarios:
        print(f"✅ Generated {len(scenarios)} training scenario(s)!\n")
        
        for i, scenario in enumerate(scenarios, 1):
            # Calculate difficulty level
            difficulty = calculate_difficulty(scenario.title, scenario.pain_summary)
            difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
            emoji = difficulty_emoji.get(difficulty, "🟡")
            
            print(f"{'─' * 80}")
            print(f"{emoji} SCENARIO {i}: {scenario.title} [{difficulty.upper()}]")
            print(f"{'─' * 80}")
            print(f"Pain Point: {scenario.pain_summary}")
            print(f"Estimated Time: {scenario.estimated_time_minutes} minutes\n")
            
            print("❌ BAD EXAMPLE:")
            for turn in scenario.bad_dialogue:
                print(f"   {turn.speaker}: \"{turn.text}\"")
            
            print("\n✅ GOOD EXAMPLE:")
            for turn in scenario.good_dialogue:
                print(f"   {turn.speaker}: \"{turn.text}\"")
            print()
        
        return scenarios
    else:
        print("❌ Failed to generate scenarios")
        print(f"Raw response: {raw}")
        return []


def demo_step_3(scenarios):
    """Demo: Practice with AI feedback and enhanced features."""
    print_section("STEP 3: PRACTICE WITH AI FEEDBACK 🎯")
    
    if not scenarios:
        print("⚠️  No scenarios available. Skipping practice session.")
        return None
    
    scenario = scenarios[0]
    business_name = "Gary Danko"
    location = "San Francisco, CA"
    business_type = "Restaurant"
    
    print(f"🎯 Practicing: {scenario.title}")
    print(f"Pain Point: {scenario.pain_summary}\n")
    
    if scenario.bad_dialogue:
        customer_line = scenario.bad_dialogue[0].text
        print(f"💬 CUSTOMER SAYS:")
        print(f'   "{customer_line}"\n')
    
    scores = []
    
    print("─" * 80)
    print("DEMO 1: Poor Staff Response")
    print("─" * 80)
    poor_response = "Sorry, we're fully booked. Try calling next month."
    print(f"📝 STAFF RESPONSE:")
    print(f'   "{poor_response}"\n')
    
    print("🤖 Getting AI feedback...")
    feedback1, _ = evaluate_staff_reply(
        business_name, location, business_type, scenario, poor_response
    )
    
    if feedback1 and feedback1.score is not None:
        scores.append(feedback1.score)
        print(f"\n📊 SCORE: {feedback1.score:.1f}/10 ", end="")
        if feedback1.score >= 8:
            print("🎉")
        elif feedback1.score >= 6:
            print("👍")
        else:
            print("📚")
        
        print(f"📝 Summary: {feedback1.summary}\n")
        
        if feedback1.strengths:
            print("✅ Strengths:")
            for strength in feedback1.strengths:
                print(f"   • {strength}")
        
        if feedback1.improvements:
            print("\n💡 Improvements:")
            for improvement in feedback1.improvements:
                print(f"   • {improvement}")
        
        badges = award_badges_for_score(feedback1.score)
        if badges:
            print("\n🏆 Badges Earned:")
            for badge in badges:
                print(f"   {badge}")
    
    print("\n")
    
    print("─" * 80)
    print("DEMO 2: Good Staff Response")
    print("─" * 80)
    good_response = (
        "I completely understand how frustrating that must be - our reservations "
        "do fill up quickly due to high demand. Let me help you right now. I can "
        "check our cancellation list for your preferred dates and add you to our "
        "priority callback list. We also have bar seating available most evenings "
        "without reservations if you'd like to experience our menu sooner. What "
        "dates were you hoping for?"
    )
    print(f"📝 STAFF RESPONSE:")
    print(f'   "{good_response}"\n')
    
    print("🤖 Getting AI feedback...")
    feedback2, _ = evaluate_staff_reply(
        business_name, location, business_type, scenario, good_response
    )
    
    if feedback2 and feedback2.score is not None:
        scores.append(feedback2.score)
        print(f"\n📊 SCORE: {feedback2.score:.1f}/10 ", end="")
        if feedback2.score >= 8:
            print("🎉")
        elif feedback2.score >= 6:
            print("👍")
        else:
            print("📚")
        
        print(f"📝 Summary: {feedback2.summary}\n")
        
        if feedback2.strengths:
            print("✅ Strengths:")
            for strength in feedback2.strengths:
                print(f"   • {strength}")
        
        if feedback2.improvements:
            print("\n💡 Improvements:")
            for improvement in feedback2.improvements:
                print(f"   • {improvement}")
        
        badges = award_badges_for_score(feedback2.score)
        if badges:
            print("\n🏆 Badges Earned:")
            for badge in badges:
                print(f"   {badge}")
    
    return scores


def demo_enhanced_features(scores):
    """Demo: Show enhanced features."""
    print_section("BONUS: ENHANCED FEATURES 🚀")
    
    print("📊 Progress Tracking:")
    tracker = ProgressTracker()
    print(f"   • Total attempts: {tracker.get_total_attempts()}")
    print(f"   • Average score: {tracker.get_average_score():.1f}/10")
    print(f"   • Badges earned: {len(tracker.get_badges())}")
    
    if tracker.get_badges():
        print("\n🏆 Your Badges:")
        for badge in tracker.get_badges():
            print(f"   🏅 {badge}")
    
    if scores:
        avg = sum(scores) / len(scores)
        print(f"\n📈 Session Stats:")
        print(f"   • Scenarios practiced: {len(scores)}")
        print(f"   • Session average: {avg:.1f}/10")
        if len(scores) >= 2:
            improvement = scores[-1] - scores[0]
            if improvement > 0:
                print(f"   • Improvement: +{improvement:.1f} points 📈")
            elif improvement < 0:
                print(f"   • Trend: {improvement:.1f} points 📉")
            else:
                print(f"   • Consistent performance ➡️")
    
    print("\n✨ Additional Features Available:")
    print("   • 🏆 Leaderboard - Team rankings and competition")
    print("   • 🎓 Certification - Bronze/Silver/Gold levels")
    print("   • 📄 Reports - Download training session reports")
    print("   • 📊 Analytics - Detailed charts and trends")
    print("   • 🎯 Difficulty Levels - Easy/Medium/Hard scenarios")


def main():
    """Run the complete demo."""
    print("\n" + "=" * 80)
    print("  🏋️  YELP REVIEW GYM - INTERACTIVE DEMO")
    print("=" * 80)
    print("\nThis demo showcases YelpReviewGym features:")
    print("  1️⃣  Analyze business reviews to find pain points")
    print("  2️⃣  Generate training scenarios with difficulty levels")
    print("  3️⃣  Practice responses and get AI feedback with badges")
    print("  4️⃣  Track progress and view enhanced features")
    print("\n⏱️  This will take about 30-60 seconds (calling Yelp AI API)...")
    print("\n" + "=" * 80)
    
    try:
        insights = demo_step_1()
        
        if insights:
            scenarios = demo_step_2(insights)
            
            if scenarios:
                scores = demo_step_3(scenarios)
                
                if scores:
                    demo_enhanced_features(scores)
        
        print_section("DEMO COMPLETE! 🎉")
        print("You've seen how YelpReviewGym:")
        print("  ✅ Analyzes real Yelp reviews to find patterns")
        print("  ✅ Creates custom training scenarios with difficulty levels")
        print("  ✅ Provides instant AI feedback with badges and scoring")
        print("  ✅ Tracks progress, achievements, and improvement")
        print("\n🚀 Ready to try the full experience?")
        print("\n   Standard Version:")
        print("   $ uv run streamlit run run_app.py")
        print("\n   Enhanced Version (RECOMMENDED):")
        print("   $ uv run streamlit run run_app_enhanced.py")
        print("\n   Or use interactive menu:")
        print("   $ ./launch.sh")
        print("\n📖 Full documentation: README_YELP_GYM.md")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("\nMake sure:")
        print("  1. YELP_API_KEY is set in .env file")
        print("  2. You have internet connection")
        print("  3. Dependencies are installed (uv sync)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
