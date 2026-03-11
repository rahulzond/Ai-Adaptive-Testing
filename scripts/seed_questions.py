"""
Seed Script — populates the 'questions' collection with 25 GRE-style questions
covering: Algebra, Arithmetic, Vocabulary, Data Interpretation, Probability.

Usage:
    python scripts/seed_questions.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import get_questions_collection

QUESTIONS = [
    # ── Arithmetic (difficulty 0.1 – 0.3) ────────────────────────────────────
    {
        "_id": "q1",
        "question_text": "What is 8 + 5?",
        "options": ["10", "11", "12", "13"],
        "correct_answer": "13",
        "difficulty": 0.1,
        "topic": "Arithmetic",
        "tags": ["addition", "numbers"],
    },
    {
        "_id": "q2",
        "question_text": "What is 15 – 7?",
        "options": ["6", "7", "8", "9"],
        "correct_answer": "8",
        "difficulty": 0.1,
        "topic": "Arithmetic",
        "tags": ["subtraction", "numbers"],
    },
    {
        "_id": "q3",
        "question_text": "What is 6 × 7?",
        "options": ["36", "42", "48", "54"],
        "correct_answer": "42",
        "difficulty": 0.2,
        "topic": "Arithmetic",
        "tags": ["multiplication"],
    },
    {
        "_id": "q4",
        "question_text": "What is 144 ÷ 12?",
        "options": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "difficulty": 0.2,
        "topic": "Arithmetic",
        "tags": ["division"],
    },
    {
        "_id": "q5",
        "question_text": "What is 20% of 150?",
        "options": ["20", "25", "30", "35"],
        "correct_answer": "30",
        "difficulty": 0.3,
        "topic": "Arithmetic",
        "tags": ["percentage", "fractions"],
    },
    # ── Algebra (difficulty 0.3 – 0.6) ────────────────────────────────────────
    {
        "_id": "q6",
        "question_text": "Solve for x: 2x + 3 = 11",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "4",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["linear equations"],
    },
    {
        "_id": "q7",
        "question_text": "What is the value of x² when x = 7?",
        "options": ["14", "42", "49", "56"],
        "correct_answer": "49",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["exponents"],
    },
    {
        "_id": "q8",
        "question_text": "Simplify: 3(x + 4) – 2x",
        "options": ["x + 4", "x + 12", "5x + 12", "x – 12"],
        "correct_answer": "x + 12",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["simplification", "expressions"],
    },
    {
        "_id": "q9",
        "question_text": "If f(x) = 2x – 1, what is f(5)?",
        "options": ["7", "8", "9", "10"],
        "correct_answer": "9",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["functions"],
    },
    {
        "_id": "q10",
        "question_text": "Solve: x² – 5x + 6 = 0. What are the roots?",
        "options": ["1 and 6", "2 and 3", "-2 and -3", "2 and -3"],
        "correct_answer": "2 and 3",
        "difficulty": 0.5,
        "topic": "Algebra",
        "tags": ["quadratic", "factoring"],
    },
    {
        "_id": "q11",
        "question_text": "If 3x – 2y = 12 and x = 4, what is y?",
        "options": ["0", "1", "2", "3"],
        "correct_answer": "0",
        "difficulty": 0.5,
        "topic": "Algebra",
        "tags": ["systems of equations"],
    },
    {
        "_id": "q12",
        "question_text": "What is the slope of the line 4x – 2y = 8?",
        "options": ["1", "2", "4", "-2"],
        "correct_answer": "2",
        "difficulty": 0.6,
        "topic": "Algebra",
        "tags": ["slope", "linear equations"],
    },
    # ── Probability (difficulty 0.5 – 0.8) ────────────────────────────────────
    {
        "_id": "q13",
        "question_text": "A fair coin is flipped. What is the probability of getting heads?",
        "options": ["0.25", "0.5", "0.75", "1.0"],
        "correct_answer": "0.5",
        "difficulty": 0.2,
        "topic": "Probability",
        "tags": ["basic probability", "coins"],
    },
    {
        "_id": "q14",
        "question_text": "A bag contains 3 red and 7 blue balls. What is the probability of drawing a red ball?",
        "options": ["0.2", "0.3", "0.4", "0.7"],
        "correct_answer": "0.3",
        "difficulty": 0.4,
        "topic": "Probability",
        "tags": ["probability", "combinations"],
    },
    {
        "_id": "q15",
        "question_text": "Two dice are rolled. What is the probability that the sum equals 7?",
        "options": ["1/6", "1/9", "1/12", "1/4"],
        "correct_answer": "1/6",
        "difficulty": 0.6,
        "topic": "Probability",
        "tags": ["dice", "probability"],
    },
    {
        "_id": "q16",
        "question_text": "In how many ways can 4 books be arranged on a shelf?",
        "options": ["12", "16", "24", "32"],
        "correct_answer": "24",
        "difficulty": 0.7,
        "topic": "Probability",
        "tags": ["permutations", "combinatorics"],
    },
    # ── Vocabulary (difficulty 0.4 – 0.9) ─────────────────────────────────────
    {
        "_id": "q17",
        "question_text": "Choose the word closest in meaning to 'EPHEMERAL':",
        "options": ["Permanent", "Transient", "Rigid", "Vast"],
        "correct_answer": "Transient",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE words"],
    },
    {
        "_id": "q18",
        "question_text": "Choose the word closest in meaning to 'LOQUACIOUS':",
        "options": ["Silent", "Talkative", "Aggressive", "Fragile"],
        "correct_answer": "Talkative",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE words"],
    },
    {
        "_id": "q19",
        "question_text": "What is the antonym of 'BENEVOLENT'?",
        "options": ["Kind", "Generous", "Malevolent", "Caring"],
        "correct_answer": "Malevolent",
        "difficulty": 0.6,
        "topic": "Vocabulary",
        "tags": ["antonyms", "GRE words"],
    },
    {
        "_id": "q20",
        "question_text": "Choose the word closest in meaning to 'OBFUSCATE':",
        "options": ["Clarify", "Confuse", "Simplify", "Emphasize"],
        "correct_answer": "Confuse",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE words"],
    },
    {
        "_id": "q21",
        "question_text": "What does 'PERSPICACIOUS' mean?",
        "options": ["Sweaty", "Quick-witted and insightful", "Argumentative", "Timid"],
        "correct_answer": "Quick-witted and insightful",
        "difficulty": 0.9,
        "topic": "Vocabulary",
        "tags": ["GRE words", "definitions"],
    },
    # ── Data Interpretation (difficulty 0.5 – 1.0) ────────────────────────────
    {
        "_id": "q22",
        "question_text": (
            "A company's revenue grew from $200,000 in 2022 to $250,000 in 2023. "
            "What is the percentage increase?"
        ),
        "options": ["20%", "25%", "30%", "50%"],
        "correct_answer": "25%",
        "difficulty": 0.5,
        "topic": "Data Interpretation",
        "tags": ["percentage change", "business math"],
    },
    {
        "_id": "q23",
        "question_text": (
            "The mean of five numbers is 12. Four of the numbers are 10, 11, 13, and 14. "
            "What is the fifth number?"
        ),
        "options": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "difficulty": 0.6,
        "topic": "Data Interpretation",
        "tags": ["mean", "statistics"],
    },
    {
        "_id": "q24",
        "question_text": (
            "A pie chart shows 40% of students prefer Math, 35% prefer Science, "
            "and the rest prefer Arts. What percentage prefers Arts?"
        ),
        "options": ["15%", "20%", "25%", "30%"],
        "correct_answer": "25%",
        "difficulty": 0.6,
        "topic": "Data Interpretation",
        "tags": ["pie charts", "percentages"],
    },
    {
        "_id": "q25",
        "question_text": (
            "A dataset has values: 4, 8, 15, 16, 23, 42. "
            "What is the median?"
        ),
        "options": ["14", "15", "15.5", "16"],
        "correct_answer": "15.5",
        "difficulty": 0.8,
        "topic": "Data Interpretation",
        "tags": ["median", "statistics"],
    },
]


def seed():
    col = get_questions_collection()
    inserted = 0
    skipped = 0

    for q in QUESTIONS:
        existing = col.find_one({"_id": q["_id"]})
        if existing:
            skipped += 1
        else:
            col.insert_one(q)
            inserted += 1

    print(f"✅ Seeding complete — {inserted} inserted, {skipped} already existed.")


if __name__ == "__main__":
    seed()
