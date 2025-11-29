"""
YelpReviewGym Streamlit App

A tool to help business owners train their staff using Yelp reviews.
"""

import streamlit as st

from .insights_service import (
    analyze_business,
    generate_scenarios,
    evaluate_staff_reply,
)
from .schemas import BusinessInsights, TrainingScenario


def main():
    st.set_page_config(
        page_title="Yelp Review Gym",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("💪 Yelp Review Gym")
    st.markdown(
        "Train your staff by analyzing Yelp reviews, generating practice scenarios, "
        "and getting real-time feedback."
    )

    # Initialize session state
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

    # Business input section
    st.markdown("### 🏢 Business Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        business_name = st.text_input("Business Name", placeholder="e.g., Joe's Pizza")
    with col2:
        location = st.text_input("Location", placeholder="e.g., San Francisco, CA")
    with col3:
        business_type = st.text_input(
            "Type (optional)", placeholder="e.g., Restaurant"
        )

    st.markdown("---")

    # Three-column layout
    col_insights, col_scenarios, col_training = st.columns(3)

    # ========== COLUMN 1: INSIGHTS ==========
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
                    # Clear downstream state
                    st.session_state.scenarios = []
                    st.session_state.scenarios_raw = ""
                    st.session_state.selected_scenario_idx = None

        # Display insights
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

    # ========== COLUMN 2: SCENARIOS ==========
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
                st.session_state.scenarios = scenarios
                st.session_state.scenarios_raw = raw
                st.session_state.selected_scenario_idx = None

        # Display scenarios
        scenarios: list[TrainingScenario] = st.session_state.scenarios
        if scenarios:
            st.success(f"✅ {len(scenarios)} scenario(s) generated!")

            for idx, scenario in enumerate(scenarios):
                with st.expander(f"📝 {scenario.title}", expanded=(idx == 0)):
                    st.markdown(f"**Pain point:** {scenario.pain_summary}")

                    st.markdown("**❌ Bad Example:**")
                    for turn in scenario.bad_dialogue:
                        st.markdown(f"- **{turn.speaker}:** {turn.text}")

                    st.markdown("**✅ Good Example:**")
                    for turn in scenario.good_dialogue:
                        st.markdown(f"- **{turn.speaker}:** {turn.text}")

                    if st.button(
                        f"Practice this scenario →",
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

    # ========== COLUMN 3: TRAINING ==========
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
                        st.markdown("---")
                        st.markdown("### 📈 Your Feedback")

                        # Score with color
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


if __name__ == "__main__":
    main()
