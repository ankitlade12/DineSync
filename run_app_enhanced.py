"""YelpReviewGym Pro - Enhanced Training Platform

Enterprise features including progress tracking, leaderboard, 
analytics, certification system, and comprehensive reporting.
"""

import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

import streamlit as st
from datetime import datetime

from yelpreviewgym.insights_service import (
    analyze_business,
    generate_scenarios,
    evaluate_staff_reply,
)
from yelpreviewgym.schemas import BusinessInsights, TrainingScenario
from yelpreviewgym.user_manager import UserManager
from yelpreviewgym.enhanced_features import (
    ProgressTracker,
    LeaderboardManager,
    CertificationSystem,
    ReportGenerator,
    calculate_difficulty,
    award_badges_for_score,
)


def main():
    st.set_page_config(
        page_title="Yelp Review Gym Pro",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "insights" not in st.session_state:
        st.session_state.insights = None
    if "insights_raw" not in st.session_state:
        st.session_state.insights_raw = ""
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = []
    if "scenarios_raw" not in st.session_state:
        st.session_state.scenarios_raw = ""
    if "selected_scenario_idx" not in st.session_state:
        st.session_state.selected_scenario_idx = None
    if "session_scores" not in st.session_state:
        st.session_state.session_scores = []
    if "completed_scenarios" not in st.session_state:
        st.session_state.completed_scenarios = set()
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if "username" not in st.session_state:
        st.session_state.username = "User"
    if "business_name" not in st.session_state:
        st.session_state.business_name = ""

    progress = ProgressTracker()
    leaderboard = LeaderboardManager()
    cert_system = CertificationSystem()
    user_manager = UserManager()

    with st.sidebar:
        st.title("💪 YelpReviewGym Pro")
        
        st.markdown("### 👤 User Profile")
        username = st.text_input("Your Name", value=st.session_state.username, key="user_input", 
                                 help="Enter a unique username (3-20 characters)")
        
        # Validate username
        if username != st.session_state.username:
            username_clean = username.strip()
            if len(username_clean) < 3:
                st.error("⚠️ Username must be at least 3 characters")
            elif len(username_clean) > 20:
                st.error("⚠️ Username must be 20 characters or less")
            elif not username_clean.replace(" ", "").replace("_", "").isalnum():
                st.error("⚠️ Username can only contain letters, numbers, spaces, and underscores")
            else:
                st.session_state.username = username_clean
                # Load user stats when username changes
                user_stats = user_manager.get_user_stats(username_clean)
                if user_stats["total_attempts"] > 0:
                    st.success(f"👋 Welcome back! You've completed {user_stats['completed_businesses']} businesses.")
        
        # Show user statistics
        user_stats = user_manager.get_user_stats(st.session_state.username)
        
        st.markdown("---")
        
        st.markdown("### 📊 Your Progress")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Attempts", user_stats["total_attempts"])
            st.metric("Businesses Trained", user_stats["total_businesses"])
        with col2:
            st.metric("Avg Score", f"{user_stats['avg_score']:.1f}/10")
            st.metric("Completed", user_stats["completed_businesses"])
        
        # Show certificates
        certificates = user_manager.get_user_certificates(st.session_state.username)
        if certificates:
            st.markdown("### 🎓 Certificates")
            for cert in certificates[-3:]:  # Show last 3
                st.markdown(f"✅ **{cert['business_name']}** ({cert['avg_score']:.1f}/10)")
        
        # Export user data
        st.markdown("---")
        if st.button("📥 Export My Data", use_container_width=True):
            import json
            user_data = user_manager.get_or_create_user(st.session_state.username)
            export_data = json.dumps(user_data, indent=2)
            st.download_button(
                label="💾 Download JSON",
                data=export_data,
                file_name=f"{st.session_state.username}_training_data.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Reset user profile
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        with st.expander("🗑️ Reset Profile"):
            st.warning("⚠️ This will delete ALL your training data, scores, and certificates permanently!")
            confirm_text = st.text_input("Type your username to confirm:", key="reset_confirm")
            if st.button("🗑️ DELETE ALL MY DATA", type="secondary", use_container_width=True):
                if confirm_text.strip() == st.session_state.username.strip():
                    # Delete user from database using the proper method
                    user_manager.delete_user(st.session_state.username)
                    
                    # Reset session state
                    st.session_state.insights = None
                    st.session_state.insights_raw = ""
                    st.session_state.scenarios = []
                    st.session_state.scenarios_raw = ""
                    st.session_state.completed_scenarios = set()
                    st.session_state.session_scores = []
                    st.session_state.selected_scenario_idx = None
                    st.session_state.username = "User"
                    st.session_state.business_name = ""
                    st.success("✅ Profile deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Username doesn't match. Reset cancelled.")
        
        # Get badges from old system
        badges = progress.get_badges()
        if badges:
            st.markdown("### 🏆 Badges Earned")
            for badge in badges:
                st.markdown(f"🏅 **{badge}**")
        
        st.markdown("---")
        
        # Show business-specific resume option if applicable
        if st.session_state.business_name:
            saved_progress = user_manager.get_business_progress(
                st.session_state.username, 
                st.session_state.business_name
            )
            if saved_progress and not saved_progress.get("completed", False):
                if st.button("🔄 Resume Training", type="secondary"):
                    st.info(f"Resuming {saved_progress['attempts']} previous attempts...")

    st.title("💪 Yelp Review Gym - Professional Edition")
    st.markdown(
        "Train your staff by analyzing Yelp reviews, generating practice scenarios, "
        "and getting real-time AI feedback. **Now with progress tracking and gamification!**"
    )
    
    # Quick stats banner
    if st.session_state.username and len(st.session_state.username.strip()) >= 3:
        user_stats = user_manager.get_user_stats(st.session_state.username)
        if user_stats["total_attempts"] > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Your Attempts", user_stats["total_attempts"])
            with col2:
                st.metric("📊 Your Avg Score", f"{user_stats['avg_score']:.1f}/10")
            with col3:
                st.metric("🏢 Businesses", user_stats["total_businesses"])
            with col4:
                global_lb = user_manager.get_all_users_leaderboard()
                your_rank = next((i for i, u in enumerate(global_lb, 1) if u['username'] == st.session_state.username), None)
                if your_rank:
                    st.metric("🏆 Global Rank", f"#{your_rank}")
            st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Training", "📈 Analytics", "🏆 Leaderboard", "📄 Reports"])

    with tab1:
        st.markdown("### 🏢 Business Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            business_name = st.text_input("Business Name", placeholder="e.g., Joe's Pizza")
            if business_name:
                st.session_state.business_name = business_name
        with col2:
            location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
        with col3:
            business_type = st.text_input(
                "Type (optional)", placeholder="e.g., Restaurant"
            )

        st.markdown("---")

        col_insights, col_scenarios, col_training = st.columns(3)

        with col_insights:
            st.markdown("### 📊 Step 1: Analyze Reviews")
            st.markdown("Discover patterns in customer delights and pain points.")
            
            # Check for saved progress
            saved_progress = user_manager.get_business_progress(
                st.session_state.username, 
                business_name.strip()
            )
            
            if saved_progress and not saved_progress.get("completed", False):
                st.info(f"📂 You have {saved_progress['attempts']} saved attempt(s) for this business. "
                       f"({len(saved_progress['completed_scenarios'])}/{saved_progress['total_scenarios']} scenarios completed)")
                col_load, col_restart = st.columns(2)
                with col_load:
                    load_saved = st.button("🔄 Continue Training", type="secondary", use_container_width=True)
                with col_restart:
                    restart_new = st.button("🆕 Start Fresh", type="secondary", use_container_width=True)
                
                if restart_new:
                    user_manager.clear_business_progress(st.session_state.username, business_name.strip())
                    st.rerun()

            if st.button("🔍 Analyze Business", type="primary", use_container_width=True):
                if not business_name.strip() or not location.strip():
                    st.error("⚠️ Please provide both Business Name and Location.")
                elif not st.session_state.username or len(st.session_state.username.strip()) < 3:
                    st.error("⚠️ Please enter a valid username first (3+ characters)")
                else:
                    progress_bar = st.progress(0, text="Starting analysis...")
                    try:
                        progress_bar.progress(25, text="Connecting to Yelp AI...")
                        insights, raw = analyze_business(
                                business_name, location, business_type
                            )
                        progress_bar.progress(75, text="Processing insights...")
                        if insights is None:
                            progress_bar.progress(100, text="Analysis failed")
                            st.error("❌ Failed to analyze business. Please check your API key and try again.")
                            st.info("💡 Make sure YELP_API_KEY is set in your .env file")
                        else:
                            progress_bar.progress(100, text="Analysis complete!")
                            st.session_state.insights = insights
                            st.session_state.insights_raw = raw
                            st.session_state.scenarios = []
                            st.session_state.scenarios_raw = ""
                            st.session_state.selected_scenario_idx = None
                            st.session_state.session_scores = []
                            st.session_state.completed_scenarios = set()
                            st.session_state.session_start_time = datetime.now()
                            st.success("✅ Analysis complete! Proceed to Step 2 to generate scenarios.")
                        progress_bar.empty()
                    except Exception as e:
                        progress_bar.empty()
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Please check your API key and internet connection")

            insights: BusinessInsights | None = st.session_state.insights
            if insights:
                st.success("✅ Analysis complete!")

                with st.expander("🌟 Delights", expanded=True):
                    if insights.delights:
                        for d in insights.delights:
                            st.markdown(f"- {d}")
                    else:
                        st.info("No delights found.")

                with st.expander("😰 Pain Points", expanded=True):
                    if insights.pains:
                        for p in insights.pains:
                            st.markdown(f"- {p}")
                    else:
                        st.info("No pain points found.")

                with st.expander("👥 Customer Personas", expanded=True):
                    if insights.personas:
                        for persona in insights.personas:
                            st.markdown(f"- {persona}")
                    else:
                        st.info("No personas found.")

                with st.expander("🔍 Raw AI Response"):
                    st.code(st.session_state.insights_raw, language="json")
            else:
                st.info("👈 Click 'Analyze Business' to begin.")

        with col_scenarios:
            st.markdown("### 🎭 Step 2: Generate Scenarios")
            st.markdown("Create practice dialogues based on pain points.")

            can_generate = (
                st.session_state.insights is not None
                and st.session_state.insights.pains
            )

            if st.button(
                "🎬 Generate Scenarios",
                type="primary",
                use_container_width=True,
                disabled=not can_generate,
            ):
                insights_obj: BusinessInsights = st.session_state.insights
                with st.spinner("Generating training scenarios..."):
                    try:
                        scenarios, raw = generate_scenarios(
                            business_name, location, business_type, insights_obj.pains
                        )
                        
                        if not scenarios:
                            st.warning("⚠️ No scenarios generated. This might be due to API limitations.")
                            st.info("💡 Try with a different business or check your API key")
                            st.session_state.scenarios = []
                            st.session_state.scenarios_raw = raw if raw else "No response"
                        else:
                            for scenario in scenarios:
                                scenario.difficulty_level = calculate_difficulty(
                                    scenario.title, scenario.pain_summary
                                )
                            
                            st.session_state.scenarios = scenarios
                            st.session_state.scenarios_raw = raw
                            st.session_state.selected_scenario_idx = None
                    except Exception as e:
                        st.error(f"❌ Error generating scenarios: {str(e)}")
                        st.info("💡 Please try again or check your API connection")

            scenarios: list[TrainingScenario] = st.session_state.scenarios
            if scenarios:
                completed_count = len(st.session_state.completed_scenarios)
                st.success(f"✅ {len(scenarios)} scenario(s) generated! ({completed_count}/{len(scenarios)} completed)")
                
                # Visual progress bar
                progress_percentage = completed_count / len(scenarios)
                st.progress(progress_percentage, text=f"Progress: {completed_count}/{len(scenarios)} scenarios completed")

                for idx, scenario in enumerate(scenarios):
                    is_completed = idx in st.session_state.completed_scenarios
                    diff_color = {
                        "easy": "🟢",
                        "medium": "🟡",
                        "hard": "🔴"
                    }
                    diff_emoji = diff_color.get(scenario.difficulty_level, "🟡")
                    completion_emoji = "✅" if is_completed else "⏳"
                    
                    with st.expander(f"{completion_emoji} {diff_emoji} {scenario.title}", expanded=(idx == 0)):
                        st.caption(f"Difficulty: {scenario.difficulty_level.upper()}")
                        st.markdown(f"**Pain point:** {scenario.pain_summary}")

                        st.markdown("**❌ Bad Example:**")
                        for turn in scenario.bad_dialogue:
                            st.markdown(f"- **{turn.speaker}:** {turn.text}")

                        st.markdown("**✅ Good Example:**")
                        for turn in scenario.good_dialogue:
                            st.markdown(f"- **{turn.speaker}:** {turn.text}")

                        if st.button(
                            "Practice this scenario →",
                            key=f"practice_{idx}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_scenario_idx = idx
                            st.rerun()

                with st.expander("🔍 Raw AI Response"):
                    st.code(st.session_state.scenarios_raw, language="json")
            else:
                if can_generate:
                    st.info("👈 Click 'Generate Scenarios' to continue.")
                else:
                    st.info("Complete Step 1 first to generate scenarios.")

        with col_training:
            st.markdown("### 🎯 Step 3: Practice & Get Feedback")
            st.markdown("Role-play as staff and receive AI coaching.")

            selected_idx = st.session_state.selected_scenario_idx
            if selected_idx is not None and 0 <= selected_idx < len(
                st.session_state.scenarios
            ):
                scenario: TrainingScenario = st.session_state.scenarios[selected_idx]

                st.markdown(f"**Scenario:** {scenario.title}")
                st.markdown(f"**Pain point:** {scenario.pain_summary}")

                st.markdown("---")
                st.markdown("**Customer says:**")
                if scenario.bad_dialogue:
                    customer_line = scenario.bad_dialogue[0].text
                    st.info(f'"{customer_line}"')
                else:
                    st.info("(No customer dialogue available)")

                st.markdown("**Your response as staff:**")
                staff_reply = st.text_area(
                    "Type your reply:",
                    placeholder="How would you handle this situation?",
                    height=120,
                    label_visibility="collapsed",
                )

                if st.button("💬 Get Feedback", type="primary", use_container_width=True):
                    if not staff_reply.strip():
                        st.error("Please write a response first.")
                    else:
                        with st.spinner("Analyzing your response..."):
                            feedback, raw = evaluate_staff_reply(
                                business_name,
                                location,
                                business_type,
                                scenario,
                                staff_reply,
                            )

                        if feedback and feedback.score is not None:
                            progress.record_attempt(
                                business_name, scenario.title, feedback.score
                            )
                            leaderboard.update_user_score(
                                st.session_state.username, feedback.score, scenario.title
                            )
                            st.session_state.session_scores.append(feedback.score)
                            
                            # Track completed scenarios
                            st.session_state.completed_scenarios.add(selected_idx)
                            
                            # Save user progress
                            scenario_titles = [s.title for s in st.session_state.scenarios]
                            user_manager.save_business_progress(
                                st.session_state.username,
                                business_name,
                                location,
                                business_type,
                                len(st.session_state.scenarios),
                                st.session_state.completed_scenarios,
                                st.session_state.session_scores,
                                scenario_titles
                            )
                            
                            new_badges = award_badges_for_score(feedback.score)
                            
                            st.markdown("---")
                            st.markdown("### 📈 Your Feedback")

                            score = feedback.score
                            if score >= 8:
                                color = "green"
                                emoji = "🎉"
                            elif score >= 6:
                                color = "orange"
                                emoji = "👍"
                            else:
                                color = "red"
                                emoji = "📚"

                            st.markdown(
                                f"**Score:** :{color}[{score:.1f}/10] {emoji}"
                            )
                            
                            if new_badges:
                                for badge in new_badges:
                                    st.success(f"🎉 {badge}")
                            
                            st.markdown(f"**Summary:** {feedback.summary}")

                            if feedback.strengths:
                                st.markdown("**✅ Strengths:**")
                                for s in feedback.strengths:
                                    st.markdown(f"- {s}")

                            if feedback.improvements:
                                st.markdown("**💡 Improvements:**")
                                for i in feedback.improvements:
                                    st.markdown(f"- {i}")

                            with st.expander("🔍 Raw AI Response"):
                                st.code(raw, language="json")
                            
                            # Show completion status
                            st.markdown("---")
                            st.success(f"✅ **Scenario Completed!** ({len(st.session_state.completed_scenarios)}/{len(st.session_state.scenarios)} done)")
                            
                            # Button to go to next incomplete scenario
                            next_incomplete = None
                            for idx in range(len(st.session_state.scenarios)):
                                if idx not in st.session_state.completed_scenarios:
                                    next_incomplete = idx
                                    break
                            
                            if next_incomplete is not None:
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🔄 Practice Another Scenario", type="primary", use_container_width=True):
                                        st.session_state.selected_scenario_idx = next_incomplete
                                        st.rerun()
                                with col2:
                                    if st.button("📊 View Progress", type="secondary", use_container_width=True):
                                        st.session_state.selected_scenario_idx = None
                                        st.rerun()
                            
                            # Check if all scenarios are completed
                            total_scenarios = len(st.session_state.scenarios)
                            completed_count = len(st.session_state.completed_scenarios)
                            
                            if completed_count == total_scenarios and total_scenarios > 0:
                                st.markdown("---")
                                
                                session_avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
                                
                                # Check if score meets certification requirement
                                CERTIFICATION_THRESHOLD = 8.0
                                
                                if session_avg >= CERTIFICATION_THRESHOLD:
                                    # Award certificate - score is high enough!
                                    st.balloons()
                                    st.success("🎓 **Congratulations! You've completed all scenarios with excellent performance!**")
                                    
                                    user_manager.award_certificate(
                                        st.session_state.username,
                                        business_name,
                                        session_avg
                                    )
                                    
                                    st.markdown(f"""
                                    ### 🏆 Training Session Complete - Certificate Earned!
                                    
                                    - **Total Scenarios:** {total_scenarios}
                                    - **Average Score:** {session_avg:.1f}/10 ✅
                                    - **Business:** {business_name}
                                    - **Duration:** {(datetime.now() - st.session_state.session_start_time).seconds // 60} minutes
                                    """)
                                    
                                    if st.button("📜 Generate Completion Certificate", type="primary"):
                                        cert_text = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🏆 CERTIFICATE OF COMPLETION 🏆                 ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  This certifies that                                     ║
║                                                          ║
║  {st.session_state.username:^56}  ║
║                                                          ║
║  has successfully completed customer service training    ║
║  for {business_name:^50}  ║
║                                                          ║
║  Training Details:                                       ║
║  • Scenarios Completed: {total_scenarios:^34}  ║
║  • Average Score: {session_avg:.1f}/10{' ' * 36}  ║
║  • Date: {datetime.now().strftime('%B %d, %Y'):^46}  ║
║                                                          ║
║  {'-' * 56}  ║
║                                                          ║
║  Authorized by YelpReviewGym Pro                         ║
║  Powered by Yelp AI                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
                                        st.code(cert_text, language="text")
                                        st.download_button(
                                            "💾 Download Certificate",
                                            cert_text,
                                            file_name=f"certificate_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.txt",
                                            mime="text/plain"
                                        )
                                
                                else:
                                    # Score is below threshold - need to retry
                                    st.warning("📚 **Training Session Complete - Practice Required**")
                                    
                                    st.markdown(f"""
                                    ### 🎯 Keep Practicing!
                                    
                                    - **Total Scenarios:** {total_scenarios}
                                    - **Average Score:** {session_avg:.1f}/10 ⚠️
                                    - **Required Score:** {CERTIFICATION_THRESHOLD}/10
                                    - **Gap:** {CERTIFICATION_THRESHOLD - session_avg:.1f} points
                                    - **Business:** {business_name}
                                    """)
                                    
                                    st.error(f"❌ **Certificate Not Earned** - Your average score of {session_avg:.1f}/10 is below the required {CERTIFICATION_THRESHOLD}/10")
                                    
                                    st.info("""
                                    💡 **To earn your certificate:**
                                    1. Review the feedback on your responses
                                    2. Practice scenarios again to improve your scores
                                    3. Aim for consistent scores of 8.0 or higher
                                    4. You can restart training for this business anytime!
                                    """)
                                    
                                    # Show which scenarios had low scores
                                    st.markdown("#### 📊 Your Scenario Scores:")
                                    for idx, score in enumerate(st.session_state.session_scores):
                                        scenario_title = st.session_state.scenarios[idx].title if idx < len(st.session_state.scenarios) else f"Scenario {idx+1}"
                                        if score < CERTIFICATION_THRESHOLD:
                                            st.markdown(f"⚠️ **{scenario_title}**: {score:.1f}/10 - *Needs improvement*")
                                        else:
                                            st.markdown(f"✅ **{scenario_title}**: {score:.1f}/10")
                                    
                                    st.markdown("---")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("🔄 Start Fresh Training", type="primary", use_container_width=True):
                                            user_manager.clear_business_progress(st.session_state.username, business_name)
                                            st.session_state.insights = None
                                            st.session_state.scenarios = []
                                            st.session_state.completed_scenarios = set()
                                            st.session_state.session_scores = []
                                            st.rerun()
                                    with col2:
                                        if st.button("📈 View Analytics", type="secondary", use_container_width=True):
                                            st.info("Check the Analytics tab to see your progress!")
                        else:
                            st.error("Failed to parse feedback. Check raw response.")
                            with st.expander("🔍 Raw AI Response"):
                                st.code(raw)

            else:
                st.info("👈 Select a scenario from Step 2 to begin practice.")

    with tab2:
        st.markdown(f"### 📈 {st.session_state.username}'s Training Analytics")
        
        # Get user-specific data
        user = user_manager.get_or_create_user(st.session_state.username)
        user_stats = user_manager.get_user_stats(st.session_state.username)
        
        if user_stats["total_attempts"] == 0:
            st.info("No training data yet. Complete some practice sessions to see your analytics!")
        else:
            # Overall stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attempts", user_stats["total_attempts"])
            with col2:
                st.metric("Average Score", f"{user_stats['avg_score']:.1f}/10")
            with col3:
                st.metric("Businesses Trained", user_stats["total_businesses"])
            with col4:
                st.metric("Completed", user_stats["completed_businesses"])
            
            st.markdown("---")
            
            # Business-by-business breakdown
            st.markdown("#### 🏢 Your Training History")
            
            if user["businesses"]:
                for business_name, business_data in user["businesses"].items():
                    completed_emoji = "✅" if business_data.get("completed", False) else "⏳"
                    
                    with st.expander(f"{completed_emoji} {business_name}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Scenarios", f"{len(business_data['completed_scenarios'])}/{business_data['total_scenarios']}")
                        with col2:
                            if business_data['scores']:
                                avg = sum(business_data['scores']) / len(business_data['scores'])
                                st.metric("Average Score", f"{avg:.1f}/10")
                        with col3:
                            st.metric("Attempts", business_data['attempts'])
                        
                        st.caption(f"📍 {business_data.get('location', 'N/A')} - {business_data.get('business_type', 'N/A')}")
                        st.caption(f"🕒 Last trained: {business_data['last_updated'][:10]}")
                        
                        if business_data['scores']:
                            st.markdown("**Scores:** " + ", ".join([f"{s:.1f}" for s in business_data['scores']]))
            
            st.markdown("---")
            
            # Current session stats
            if st.session_state.session_scores:
                st.markdown("#### 🎯 Current Session")
                session_col1, session_col2, session_col3 = st.columns(3)
                
                with session_col1:
                    st.metric("Scenarios Practiced", len(st.session_state.session_scores))
                with session_col2:
                    session_avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
                    st.metric("Session Average", f"{session_avg:.1f}/10")
                with session_col3:
                    time_spent = (datetime.now() - st.session_state.session_start_time).seconds // 60
                    st.metric("Time Spent", f"{time_spent} min")
            
            # Certificates section
            certificates = user_manager.get_user_certificates(st.session_state.username)
            if certificates:
                st.markdown("---")
                st.markdown("#### 🎓 Your Certificates")
                
                for cert in certificates:
                    st.success(f"✅ **{cert['business_name']}** - {cert['avg_score']:.1f}/10 (Earned: {cert['display_date']})")
            
            # Performance comparison
            st.markdown("---")
            st.markdown("#### 📊 How Do You Compare?")
            
            global_leaderboard = user_manager.get_all_users_leaderboard()
            if global_leaderboard and len(global_leaderboard) > 1:
                top_performer = global_leaderboard[0]
                your_rank = None
                for idx, user in enumerate(global_leaderboard, 1):
                    if user['username'] == st.session_state.username:
                        your_rank = idx
                        break
                
                if your_rank:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Your Rank", f"#{your_rank}/{len(global_leaderboard)}")
                    with col2:
                        gap = top_performer['avg_score'] - user_stats['avg_score']
                        st.metric("Gap to #1", f"{gap:.1f} points", 
                                 delta=f"{-gap:.1f}" if gap > 0 else "You're #1! 🎉")
                    with col3:
                        if your_rank == 1:
                            st.metric("Status", "🥇 Leader!")
                        elif your_rank <= 3:
                            st.metric("Status", "🏆 Top 3!")
                        elif your_rank <= 10:
                            st.metric("Status", "⭐ Top 10!")
                        else:
                            st.metric("Status", "💪 Keep going!")
            else:
                st.info("Complete more training to see comparisons!")

    with tab3:
        st.markdown("### 🏆 Leaderboard")
        
        # Toggle between global and business-specific leaderboard
        leaderboard_type = st.radio(
            "View:",
            ["🌍 Global Rankings", "🏢 Business-Specific Rankings"],
            horizontal=True
        )
        
        if leaderboard_type == "🌍 Global Rankings":
            # Global leaderboard (existing code)
            leaderboard_data = user_manager.get_all_users_leaderboard()
            
            if not leaderboard_data:
                st.info("No leaderboard data yet. Be the first to train!")
            else:
                # Find current user's rank
                current_user_rank = None
                for idx, user_data in enumerate(leaderboard_data, 1):
                    if user_data['username'] == st.session_state.username:
                        current_user_rank = idx
                        break
                
                # Show user's rank
                if current_user_rank:
                    if current_user_rank <= 3:
                        st.success(f"🌟 You're ranked #{current_user_rank} out of {len(leaderboard_data)} users!")
                    elif current_user_rank <= 10:
                        st.info(f"📊 You're ranked #{current_user_rank} out of {len(leaderboard_data)} users")
                    else:
                        st.info(f"📊 You're ranked #{current_user_rank} out of {len(leaderboard_data)} users")
                
                st.markdown("---")
                st.markdown("**Top 10 performers across all businesses:**")
                
                for idx, user in enumerate(leaderboard_data[:10], 1):
                    medal = ""
                    if idx == 1:
                        medal = "🥇"
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    
                    # Highlight current user
                    is_current_user = user['username'] == st.session_state.username
                    
                    with st.container():
                        if is_current_user:
                            st.markdown("**👤 YOU**")
                        
                        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                        with col1:
                            st.markdown(f"### {medal} #{idx}")
                        with col2:
                            display_name = f"**{user['username']}** 👈" if is_current_user else f"**{user['username']}**"
                            st.markdown(display_name)
                        with col3:
                            st.metric("Avg Score", f"{user['avg_score']:.1f}/10")
                        with col4:
                            st.metric("Attempts", user['total_attempts'])
                        with col5:
                            st.metric("Completed", user['completed_businesses'])
                        
                        st.markdown("---")
        
        else:  # Business-Specific Rankings
            # Get all businesses
            all_businesses = user_manager.get_all_businesses()
            
            if not all_businesses:
                st.info("No businesses trained yet!")
            else:
                st.markdown("**Compare performance on specific businesses:**")
                
                # Let user select a business
                selected_business = st.selectbox(
                    "Choose a business to see rankings:",
                    all_businesses
                )
                
                if selected_business:
                    business_leaderboard = user_manager.get_business_leaderboard(selected_business)
                    
                    if not business_leaderboard:
                        st.warning(f"No training data for {selected_business}")
                    else:
                        # Find current user's rank for this business
                        current_user_rank = None
                        for idx, user_data in enumerate(business_leaderboard, 1):
                            if user_data['username'] == st.session_state.username:
                                current_user_rank = idx
                                break
                        
                        # Show user's rank for this business
                        if current_user_rank:
                            st.success(f"🏢 Your rank for **{selected_business}**: #{current_user_rank} out of {len(business_leaderboard)} users")
                        else:
                            st.info(f"You haven't trained on **{selected_business}** yet")
                        
                        st.markdown("---")
                        st.markdown(f"**Top performers for {selected_business}:**")
                        
                        for idx, user in enumerate(business_leaderboard[:10], 1):
                            medal = ""
                            if idx == 1:
                                medal = "🥇"
                            elif idx == 2:
                                medal = "🥈"
                            elif idx == 3:
                                medal = "🥉"
                            
                            # Highlight current user
                            is_current_user = user['username'] == st.session_state.username
                            completion_status = "✅" if user['completed'] else "⏳"
                            
                            with st.container():
                                if is_current_user:
                                    st.markdown("**👤 YOU**")
                                
                                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                                with col1:
                                    st.markdown(f"### {medal} #{idx}")
                                with col2:
                                    display_name = f"**{user['username']}** 👈" if is_current_user else f"**{user['username']}**"
                                    st.markdown(display_name)
                                with col3:
                                    st.metric("Avg Score", f"{user['avg_score']:.1f}/10")
                                with col4:
                                    st.metric("Progress", f"{user['completed_scenarios']}/{user['total_scenarios']} {completion_status}")
                                with col5:
                                    st.metric("Attempts", user['attempts'])
                                
                                st.markdown("---")

    with tab4:
        st.markdown(f"### 📄 {st.session_state.username}'s Training Reports")
        
        # Get user data
        user = user_manager.get_or_create_user(st.session_state.username)
        
        if not user["businesses"]:
            st.info("Complete a training session to generate reports!")
        else:
            st.markdown("#### � Select Business to Generate Report")
            
            # Let user select which business to generate report for
            business_names = list(user["businesses"].keys())
            selected_business = st.selectbox("Choose a business:", business_names)
            
            if selected_business:
                business_data = user["businesses"][selected_business]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scenarios Completed", f"{len(business_data['completed_scenarios'])}/{business_data['total_scenarios']}")
                with col2:
                    if business_data['scores']:
                        avg = sum(business_data['scores']) / len(business_data['scores'])
                        st.metric("Average Score", f"{avg:.1f}/10")
                with col3:
                    st.metric("Total Attempts", business_data['attempts'])
                
                st.markdown("---")
                
                if st.button("📊 Generate Report", type="primary"):
                    # Calculate time spent (use last_updated - started_at)
                    from datetime import datetime as dt
                    try:
                        started = dt.fromisoformat(business_data['started_at'])
                        updated = dt.fromisoformat(business_data['last_updated'])
                        time_spent = int((updated - started).total_seconds() / 60)
                    except (ValueError, KeyError):
                        time_spent = 0
                    
                    # Generate report
                    report_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    TRAINING SESSION REPORT                       ║
╚══════════════════════════════════════════════════════════════════╝

User: {st.session_state.username}
Business: {selected_business}
Location: {business_data.get('location', 'N/A')}
Business Type: {business_data.get('business_type', 'N/A')}

═══════════════════════════════════════════════════════════════════

TRAINING SUMMARY:

  • Total Scenarios: {business_data['total_scenarios']}
  • Completed Scenarios: {len(business_data['completed_scenarios'])}
  • Total Attempts: {business_data['attempts']}
  • Status: {'✅ COMPLETED' if business_data.get('completed', False) else '⏳ IN PROGRESS'}

═══════════════════════════════════════════════════════════════════

PERFORMANCE METRICS:

  • Average Score: {sum(business_data['scores']) / len(business_data['scores']):.1f}/10 if business_data['scores'] else 'N/A'
  • Highest Score: {max(business_data['scores']):.1f}/10 if business_data['scores'] else 'N/A'
  • Lowest Score: {min(business_data['scores']):.1f}/10 if business_data['scores'] else 'N/A'
  • Time Spent: ~{time_spent} minutes

═══════════════════════════════════════════════════════════════════

SCENARIO BREAKDOWN:

"""
                    for idx, title in enumerate(business_data['scenario_titles']):
                        status = "✅" if idx in business_data['completed_scenarios'] else "⏳"
                        score = business_data['scores'][idx] if idx < len(business_data['scores']) else "N/A"
                        report_text += f"  {status} {idx + 1}. {title}\n"
                        if isinstance(score, (int, float)):
                            report_text += f"     Score: {score:.1f}/10\n"
                        report_text += "\n"
                    
                    report_text += f"""
═══════════════════════════════════════════════════════════════════

TRAINING DATES:

  • Started: {business_data['started_at'][:10]}
  • Last Updated: {business_data['last_updated'][:10]}

═══════════════════════════════════════════════════════════════════

Generated by YelpReviewGym Pro
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

"""
                    
                    st.markdown("#### 📋 Your Training Report")
                    st.code(report_text, language="text")
                    
                    st.download_button(
                        label="📥 Download Report",
                        data=report_text,
                        file_name=f"training_report_{st.session_state.username}_{selected_business.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            
            # Also show current session report if active
            if st.session_state.session_scores and st.session_state.business_name:
                st.markdown("---")
                st.markdown("#### 🔄 Current Session Quick Report")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Scenarios Practiced", len(st.session_state.session_scores))
                with col2:
                    session_avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
                    st.metric("Session Average", f"{session_avg:.1f}/10")
                with col3:
                    time_spent = (datetime.now() - st.session_state.session_start_time).seconds // 60
                    st.metric("Time Spent", f"{time_spent} min")


if __name__ == "__main__":
    main()
