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
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if "username" not in st.session_state:
        st.session_state.username = "User"
    if "business_name" not in st.session_state:
        st.session_state.business_name = ""

    progress = ProgressTracker()
    leaderboard = LeaderboardManager()
    cert_system = CertificationSystem()

    with st.sidebar:
        st.title("💪 YelpReviewGym Pro")
        
        st.markdown("### 👤 User Profile")
        username = st.text_input("Your Name", value=st.session_state.username, key="user_input")
        if username != st.session_state.username:
            st.session_state.username = username
        
        st.markdown("---")
        
        st.markdown("### 📊 Your Progress")
        total_attempts = progress.get_total_attempts()
        avg_score = progress.get_average_score()
        badges = progress.get_badges()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Attempts", total_attempts)
        with col2:
            st.metric("Avg Score", f"{avg_score:.1f}/10")
        
        if badges:
            st.markdown("### 🏆 Badges Earned")
            for badge in badges:
                st.markdown(f"🏅 **{badge}**")
        else:
            st.info("Complete training to earn badges!")
        
        st.markdown("---")
        st.markdown("### 🎓 Certification")
        cert_info = cert_system.check_certification_eligibility(
            total_attempts, avg_score, badges
        )
        
        if cert_info["eligible"]:
            st.success(f"✅ **{cert_info['level']} Certified!**")
            if st.button("📜 View Certificate"):
                cert_text = cert_system.generate_certificate_text(
                    st.session_state.username,
                    cert_info["level"],
                    st.session_state.business_name or "Customer Service",
                    datetime.now().strftime("%B %d, %Y")
                )
                st.code(cert_text)
        else:
            st.warning("Not yet certified")
            if cert_info["requirements_needed"]:
                for req in cert_info["requirements_needed"]:
                    st.caption(f"• {req}")

    st.title("💪 Yelp Review Gym - Professional Edition")
    st.markdown(
        "Train your staff by analyzing Yelp reviews, generating practice scenarios, "
        "and getting real-time AI feedback. **Now with progress tracking and gamification!**"
    )

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

            if st.button("🔍 Analyze Business", type="primary", use_container_width=True):
                if not business_name.strip() or not location.strip():
                    st.error("Please provide both Business Name and Location.")
                else:
                    with st.spinner("Analyzing Yelp reviews..."):
                        insights, raw = analyze_business(
                            business_name, location, business_type
                        )
                        st.session_state.insights = insights
                        st.session_state.insights_raw = raw
                        st.session_state.scenarios = []
                        st.session_state.scenarios_raw = ""
                        st.session_state.selected_scenario_idx = None
                        st.session_state.session_scores = []
                        st.session_state.session_start_time = datetime.now()

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
                    scenarios, raw = generate_scenarios(
                        business_name, location, business_type, insights_obj.pains
                    )
                    
                    for scenario in scenarios:
                        scenario.difficulty_level = calculate_difficulty(
                            scenario.title, scenario.pain_summary
                        )
                    
                    st.session_state.scenarios = scenarios
                    st.session_state.scenarios_raw = raw
                    st.session_state.selected_scenario_idx = None

            scenarios: list[TrainingScenario] = st.session_state.scenarios
            if scenarios:
                st.success(f"✅ {len(scenarios)} scenario(s) generated!")

                for idx, scenario in enumerate(scenarios):
                    diff_color = {
                        "easy": "🟢",
                        "medium": "🟡",
                        "hard": "🔴"
                    }
                    diff_emoji = diff_color.get(scenario.difficulty_level, "🟡")
                    
                    with st.expander(f"{diff_emoji} {scenario.title}", expanded=(idx == 0)):
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
                        else:
                            st.error("Failed to parse feedback. Check raw response.")
                            with st.expander("🔍 Raw AI Response"):
                                st.code(raw)

            else:
                st.info("👈 Select a scenario from Step 2 to begin practice.")

    with tab2:
        st.markdown("### 📈 Training Analytics")
        
        if progress.get_total_attempts() == 0:
            st.info("No training data yet. Complete some practice sessions to see analytics!")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attempts", progress.get_total_attempts())
            with col2:
                st.metric("Average Score", f"{progress.get_average_score():.1f}/10")
            with col3:
                st.metric("Badges Earned", len(progress.get_badges()))
            with col4:
                recent_scores = progress.get_improvement_trend(5)
                if len(recent_scores) >= 2:
                    trend = recent_scores[-1] - recent_scores[0]
                    st.metric("Recent Trend", f"{trend:+.1f}", delta=f"{trend:.1f}")
            
            st.markdown("---")
            
            st.markdown("#### 📊 Score Trend (Last 10 Attempts)")
            trend_data = progress.get_improvement_trend(10)
            if trend_data:
                st.line_chart(trend_data)
            
            if st.session_state.session_scores:
                st.markdown("---")
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

    with tab3:
        st.markdown("### 🏆 Top Performers")
        
        top_users = leaderboard.get_top_performers(10)
        
        if not top_users:
            st.info("No leaderboard data yet. Be the first to train!")
        else:
            for idx, user in enumerate(top_users, 1):
                medal = ""
                if idx == 1:
                    medal = "🥇"
                elif idx == 2:
                    medal = "🥈"
                elif idx == 3:
                    medal = "🥉"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    with col1:
                        st.markdown(f"### {medal} #{idx}")
                    with col2:
                        st.markdown(f"**{user['username']}**")
                    with col3:
                        st.metric("Avg Score", f"{user['average_score']:.1f}/10")
                    with col4:
                        st.metric("Attempts", user['total_attempts'])
                    
                    st.markdown("---")

    with tab4:
        st.markdown("### 📄 Training Reports")
        
        if st.session_state.session_scores and st.session_state.business_name:
            st.markdown("#### 📝 Generate Session Report")
            
            if st.button("📊 Create Report", type="primary"):
                time_spent = (datetime.now() - st.session_state.session_start_time).seconds // 60
                
                insights_dict = {}
                if st.session_state.insights:
                    insights_dict = {
                        "pains": st.session_state.insights.pains,
                        "delights": st.session_state.insights.delights
                    }
                
                report = ReportGenerator.generate_session_report(
                    st.session_state.business_name,
                    insights_dict,
                    len(st.session_state.session_scores),
                    st.session_state.session_scores,
                    time_spent
                )
                
                st.markdown("#### Your Training Report")
                st.code(report)
                
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name=f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("Complete a training session to generate a report!")


if __name__ == "__main__":
    main()
