from __future__ import annotations

from typing import Dict, List, Any

from .schemas import BusinessInsights, TrainingScenario, DialogueTurn, FeedbackResult
from .yelp_ai_client import YelpAIClient
from .performance_metrics import track_performance


def build_insights_prompt(business_name: str, location: str, business_type: str) -> str:
    """Generate prompt for extracting business insights from Yelp reviews."""
    return f"""
Analyze Yelp reviews for {business_name} in {location} ({business_type}).

Find patterns and return JSON:

{{
  "delights": ["what customers love", "..."],
  "pains": ["what customers complain about", "..."],
  "personas": ["customer type 1", "customer type 2"]
}}

Keep each item under 100 characters.
""".strip()


def parse_insights_json(data: Dict[str, Any]) -> BusinessInsights:
    """Parse insights JSON response into BusinessInsights object."""
    delights = [str(x).strip() for x in data.get("delights", []) if str(x).strip()]
    pains = [str(x).strip() for x in data.get("pains", []) if str(x).strip()]
    personas = [str(x).strip() for x in data.get("personas", []) if str(x).strip()]
    return BusinessInsights(delights=delights, pains=pains, personas=personas)


def build_scenarios_prompt(
    business_name: str,
    location: str,
    business_type: str,
    pain_points: List[str],
) -> str:
    """Generate prompt for creating training scenarios from pain points.
    
    Args:
        business_name: Name of the business
        location: Business location (for context)
        business_type: Type of business (for context)
        pain_points: List of customer pain points
    """
    if not pain_points:
        pain_list = "- Customer service issues"
        num_scenarios = 1
    else:
        # Use all pain points, but limit to max 5 for API efficiency
        top_pains = pain_points[:5]
        pain_list = "\n".join(f"- {p}" for p in top_pains)
        num_scenarios = len(top_pains)
    
    return f"""
Based on Yelp reviews for {business_name} in {location} ({business_type}), create {num_scenarios} customer service training scenarios, one for each of these complaints:

{pain_list}

Return ONLY valid JSON with no additional text or explanation:

{{
  "scenarios": [
    {{
      "title": "scenario name",
      "pain_summary": "the issue",
      "bad_dialogue": [
        {{"speaker": "Customer", "text": "complaint"}},
        {{"speaker": "Staff", "text": "poor response"}}
      ],
      "good_dialogue": [
        {{"speaker": "Customer", "text": "same complaint"}},
        {{"speaker": "Staff", "text": "good response"}}
      ]
    }}
  ]
}}
""".strip()


def parse_scenarios_json(data: Dict[str, Any]) -> List[TrainingScenario]:
    """Parse scenarios JSON response into TrainingScenario objects."""
    scenarios_raw = data.get("scenarios", []) or []
    scenarios: List[TrainingScenario] = []

    for s in scenarios_raw:
        title = str(s.get("title", "")).strip() or "Untitled scenario"
        pain_summary = str(s.get("pain_summary", "")).strip()

        def parse_dialogue(key: str) -> List[DialogueTurn]:
            turns_raw = s.get(key, []) or []
            result: List[DialogueTurn] = []
            for t in turns_raw:
                speaker = str(t.get("speaker", "")).strip() or "Unknown"
                text = str(t.get("text", "")).strip()
                if text:
                    result.append(DialogueTurn(speaker=speaker, text=text))
            return result

        bad_dialogue = parse_dialogue("bad_dialogue")
        good_dialogue = parse_dialogue("good_dialogue")

        scenarios.append(
            TrainingScenario(
                title=title,
                pain_summary=pain_summary,
                bad_dialogue=bad_dialogue,
                good_dialogue=good_dialogue,
            )
        )

    return scenarios


def build_feedback_prompt(
    business_name: str,
    location: str,
    business_type: str,
    scenario: TrainingScenario,
    staff_reply: str,
) -> str:
    """Generate prompt for evaluating staff response."""
    customer_line = scenario.bad_dialogue[0].text if scenario.bad_dialogue else "Customer concern"
    good_staff = scenario.good_dialogue[1].text if len(scenario.good_dialogue) > 1 else "Show empathy and offer solutions"

    return f"""
Evaluate this customer service response for {business_name} in {location} ({business_type}).

Customer: "{customer_line}"

Staff replied: "{staff_reply}"

Good example: "{good_staff}"

Rate the staff response from 0-10 and return ONLY valid JSON with no additional text or explanation:

{{
  "score": 8.5,
  "summary": "brief assessment",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"]
}}
""".strip()


def parse_feedback_json(data: Dict[str, Any]) -> FeedbackResult:
    """Parse feedback JSON response into FeedbackResult object."""
    raw_score = data.get("score")
    score = None
    try:
        if raw_score is not None:
            score = float(raw_score)
    except (ValueError, TypeError):
        score = None

    summary = str(data.get("summary", "")).strip()
    strengths = [str(x).strip() for x in data.get("strengths", []) if str(x).strip()]
    improvements = [
        str(x).strip() for x in data.get("improvements", []) if str(x).strip()
    ]

    return FeedbackResult(
        score=score,
        summary=summary,
        strengths=strengths,
        improvements=improvements,
    )


@track_performance(metadata={"operation": "analyze_business"})
def analyze_business(
    business_name: str, location: str, business_type: str
) -> tuple[BusinessInsights | None, str]:
    """Analyze business reviews and extract insights."""
    try:
        client = YelpAIClient()
        prompt = build_insights_prompt(business_name, location, business_type)
        raw = client.chat(prompt)
        parsed_json, raw_text = YelpAIClient.json_from_response(raw)
        if parsed_json is None:
            return None, raw_text
        return parse_insights_json(parsed_json), raw_text
    except Exception as e:
        print(f"Error analyzing business: {e}")
        return None, ""


@track_performance(metadata={"operation": "generate_scenarios"})
def generate_scenarios(
    business_name: str,
    location: str,
    business_type: str,
    pain_points: List[str],
) -> tuple[List[TrainingScenario], str]:
    """Generate training scenarios based on pain points."""
    try:
        client = YelpAIClient()
        prompt = build_scenarios_prompt(business_name, location, business_type, pain_points)
        raw = client.chat(prompt)
        parsed_json, raw_text = YelpAIClient.json_from_response(raw)
        if parsed_json is None:
            return [], raw_text
        scenarios = parse_scenarios_json(parsed_json)
        return scenarios, raw_text
    except Exception as e:
        print(f"Error generating scenarios: {e}")
        import traceback
        traceback.print_exc()
        return [], ""


@track_performance(metadata={"operation": "evaluate_staff_reply"})
def evaluate_staff_reply(
    business_name: str,
    location: str,
    business_type: str,
    scenario: TrainingScenario,
    staff_reply: str,
) -> tuple[FeedbackResult, str]:
    """Evaluate staff response and provide feedback."""
    try:
        client = YelpAIClient()
        prompt = build_feedback_prompt(
            business_name, location, business_type, scenario, staff_reply
        )
        raw = client.chat(prompt)
        parsed_json, raw_text = YelpAIClient.json_from_response(raw)
        if parsed_json is None:
            return FeedbackResult(score=None, summary="", strengths=[], improvements=[]), raw_text
        feedback = parse_feedback_json(parsed_json)
        return feedback, raw_text
    except Exception as e:
        print(f"Error evaluating reply: {e}")
        import traceback
        traceback.print_exc()
        return FeedbackResult(score=None, summary="Error", strengths=[], improvements=[]), ""
