"""
AI Service — generates a personalized study plan via OpenAI ChatCompletion.
Falls back to a rule-based mock plan when OPENAI_API_KEY is not configured.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_PLACEHOLDER_KEYS = {"", "sk-...", "your-key-here"}


def _is_mock_mode() -> bool:
    return not _OPENAI_KEY or _OPENAI_KEY in _PLACEHOLDER_KEYS


def _mock_study_plan(
    final_ability: float,
    topics_missed: List[str],
    correct_count: int,
    total_questions: int,
) -> str:
    """Generate a rule-based study plan without calling any external API."""
    accuracy = round((correct_count / total_questions) * 100) if total_questions else 0
    level = "foundational" if final_ability < 0.45 else "intermediate" if final_ability < 0.7 else "advanced"
    weak = ", ".join(topics_missed) if topics_missed else "None"

    steps = [
        f"1. **Review weak topics ({weak})**: Spend 20 minutes each day revisiting the core "
        f"concepts in your missed areas using textbooks or Khan Academy.",
        f"2. **Targeted practice at {level} difficulty**: Solve 15–20 GRE-style {level} "
        f"problems daily, focusing on accuracy over speed.",
        f"3. **Mixed timed drills**: After 5 days, switch to 10-minute timed mixed-topic "
        f"sets to build exam stamina. Aim for {min(accuracy + 15, 100)}%+ accuracy.",
    ]
    header = (
        f"📊 **Your Results** — Ability: {final_ability:.2f}/1.0 | "
        f"Accuracy: {correct_count}/{total_questions} ({accuracy}%)\n\n"
        f"🗺️ **Personalized 3-Step Study Plan** (Demo Mode — add OPENAI_API_KEY for AI-generated plans)\n\n"
    )
    return header + "\n\n".join(steps)




def build_prompt(
    final_ability: float,
    topics_missed: List[str],
    correct_count: int,
    total_questions: int,
    question_history: list,
) -> str:
    """Construct the prompt sent to the LLM."""
    accuracy_pct = round((correct_count / total_questions) * 100) if total_questions else 0
    weak_topics_str = "\n".join(f"- {t}" for t in topics_missed) if topics_missed else "None"

    return (
        f"A student just completed an adaptive GRE-style diagnostic test.\n\n"
        f"Final ability score: {final_ability:.2f} (scale 0.1 – 1.0)\n"
        f"Correct answers: {correct_count}/{total_questions} ({accuracy_pct}%)\n\n"
        f"Weak topics (answered incorrectly):\n{weak_topics_str}\n\n"
        f"Based on this performance, generate a concise 3-step personalized study plan. "
        f"Each step should be actionable, specific, and tailored to the student's weak areas. "
        f"Format the output as a numbered list."
    )


def generate_study_plan(
    final_ability: float,
    topics_missed: List[str],
    correct_count: int,
    total_questions: int,
    question_history: list,
) -> str:
    """
    Generate a study plan.
    - If OPENAI_API_KEY is not set, returns a rule-based mock plan instantly.
    - Otherwise calls the OpenAI API.

    Raises:
        RuntimeError: If the OpenAI API call fails.
    """
    if _is_mock_mode():
        return _mock_study_plan(final_ability, topics_missed, correct_count, total_questions)

    from openai import OpenAI
    client = OpenAI(api_key=_OPENAI_KEY)

    prompt = build_prompt(
        final_ability, topics_missed, correct_count, total_questions, question_history
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert GRE tutor and academic coach. "
                        "Your task is to create concise, practical, and personalized study plans."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {e}")
