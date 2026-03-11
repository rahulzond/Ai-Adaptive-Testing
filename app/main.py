"""
FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.session_routes import router as session_router
from app.routes.question_routes import router as question_router
from app.routes.analytics_routes import router as analytics_router

# Absolute path to the static directory (works regardless of cwd)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


def _auto_seed():
    """
    Seed questions into the database on startup.
    When MONGO_URI is not configured the app uses mongomock (in-memory),
    so questions must be inserted inside the same process.
    When a real MongoDB is used, existing questions are skipped (idempotent).
    """
    from app.database import get_questions_collection

    QUESTIONS = [
        # ── Arithmetic ────
        {"_id": "q1", "question_text": "What is 8 + 5?", "options": ["10", "11", "12", "13"], "correct_answer": "13", "difficulty": 0.1, "topic": "Arithmetic", "tags": ["addition"]},
        {"_id": "q2", "question_text": "What is 15 – 7?", "options": ["6", "7", "8", "9"], "correct_answer": "8", "difficulty": 0.1, "topic": "Arithmetic", "tags": ["subtraction"]},
        {"_id": "q3", "question_text": "What is 6 × 7?", "options": ["36", "42", "48", "54"], "correct_answer": "42", "difficulty": 0.2, "topic": "Arithmetic", "tags": ["multiplication"]},
        {"_id": "q4", "question_text": "What is 144 ÷ 12?", "options": ["10", "11", "12", "13"], "correct_answer": "12", "difficulty": 0.2, "topic": "Arithmetic", "tags": ["division"]},
        {"_id": "q5", "question_text": "What is 20% of 150?", "options": ["20", "25", "30", "35"], "correct_answer": "30", "difficulty": 0.3, "topic": "Arithmetic", "tags": ["percentage"]},
        # ── Algebra ────
        {"_id": "q6", "question_text": "Solve for x: 2x + 3 = 11", "options": ["2", "3", "4", "5"], "correct_answer": "4", "difficulty": 0.3, "topic": "Algebra", "tags": ["linear equations"]},
        {"_id": "q7", "question_text": "What is the value of x² when x = 7?", "options": ["14", "42", "49", "56"], "correct_answer": "49", "difficulty": 0.3, "topic": "Algebra", "tags": ["exponents"]},
        {"_id": "q8", "question_text": "Simplify: 3(x + 4) – 2x", "options": ["x + 4", "x + 12", "5x + 12", "x – 12"], "correct_answer": "x + 12", "difficulty": 0.4, "topic": "Algebra", "tags": ["simplification"]},
        {"_id": "q9", "question_text": "If f(x) = 2x – 1, what is f(5)?", "options": ["7", "8", "9", "10"], "correct_answer": "9", "difficulty": 0.4, "topic": "Algebra", "tags": ["functions"]},
        {"_id": "q10", "question_text": "Solve: x² – 5x + 6 = 0. What are the roots?", "options": ["1 and 6", "2 and 3", "-2 and -3", "2 and -3"], "correct_answer": "2 and 3", "difficulty": 0.5, "topic": "Algebra", "tags": ["quadratic"]},
        {"_id": "q11", "question_text": "If 3x – 2y = 12 and x = 4, what is y?", "options": ["0", "1", "2", "3"], "correct_answer": "0", "difficulty": 0.5, "topic": "Algebra", "tags": ["systems of equations"]},
        {"_id": "q12", "question_text": "What is the slope of the line 4x – 2y = 8?", "options": ["1", "2", "4", "-2"], "correct_answer": "2", "difficulty": 0.6, "topic": "Algebra", "tags": ["slope"]},
        # ── Probability ────
        {"_id": "q13", "question_text": "A fair coin is flipped. What is the probability of getting heads?", "options": ["0.25", "0.5", "0.75", "1.0"], "correct_answer": "0.5", "difficulty": 0.2, "topic": "Probability", "tags": ["basic probability"]},
        {"_id": "q14", "question_text": "A bag contains 3 red and 7 blue balls. What is the probability of drawing a red ball?", "options": ["0.2", "0.3", "0.4", "0.7"], "correct_answer": "0.3", "difficulty": 0.4, "topic": "Probability", "tags": ["probability"]},
        {"_id": "q15", "question_text": "Two dice are rolled. What is the probability that the sum equals 7?", "options": ["1/6", "1/9", "1/12", "1/4"], "correct_answer": "1/6", "difficulty": 0.6, "topic": "Probability", "tags": ["dice"]},
        {"_id": "q16", "question_text": "In how many ways can 4 books be arranged on a shelf?", "options": ["12", "16", "24", "32"], "correct_answer": "24", "difficulty": 0.7, "topic": "Probability", "tags": ["permutations"]},
        # ── Vocabulary ────
        {"_id": "q17", "question_text": "Choose the word closest in meaning to 'EPHEMERAL':", "options": ["Permanent", "Transient", "Rigid", "Vast"], "correct_answer": "Transient", "difficulty": 0.5, "topic": "Vocabulary", "tags": ["synonyms"]},
        {"_id": "q18", "question_text": "Choose the word closest in meaning to 'LOQUACIOUS':", "options": ["Silent", "Talkative", "Aggressive", "Fragile"], "correct_answer": "Talkative", "difficulty": 0.5, "topic": "Vocabulary", "tags": ["synonyms"]},
        {"_id": "q19", "question_text": "What is the antonym of 'BENEVOLENT'?", "options": ["Kind", "Generous", "Malevolent", "Caring"], "correct_answer": "Malevolent", "difficulty": 0.6, "topic": "Vocabulary", "tags": ["antonyms"]},
        {"_id": "q20", "question_text": "Choose the word closest in meaning to 'OBFUSCATE':", "options": ["Clarify", "Confuse", "Simplify", "Emphasize"], "correct_answer": "Confuse", "difficulty": 0.7, "topic": "Vocabulary", "tags": ["synonyms"]},
        {"_id": "q21", "question_text": "What does 'PERSPICACIOUS' mean?", "options": ["Sweaty", "Quick-witted and insightful", "Argumentative", "Timid"], "correct_answer": "Quick-witted and insightful", "difficulty": 0.9, "topic": "Vocabulary", "tags": ["definitions"]},
        # ── Data Interpretation ────
        {"_id": "q22", "question_text": "A company's revenue grew from $200,000 to $250,000. What is the percentage increase?", "options": ["20%", "25%", "30%", "50%"], "correct_answer": "25%", "difficulty": 0.5, "topic": "Data Interpretation", "tags": ["percentage change"]},
        {"_id": "q23", "question_text": "The mean of five numbers is 12. Four are 10, 11, 13, 14. What is the fifth?", "options": ["10", "11", "12", "13"], "correct_answer": "12", "difficulty": 0.6, "topic": "Data Interpretation", "tags": ["mean"]},
        {"_id": "q24", "question_text": "40% prefer Math, 35% prefer Science. What percentage prefers Arts?", "options": ["15%", "20%", "25%", "30%"], "correct_answer": "25%", "difficulty": 0.6, "topic": "Data Interpretation", "tags": ["pie charts"]},
        {"_id": "q25", "question_text": "Dataset: 4, 8, 15, 16, 23, 42. What is the median?", "options": ["14", "15", "15.5", "16"], "correct_answer": "15.5", "difficulty": 0.8, "topic": "Data Interpretation", "tags": ["median"]},
    ]

    col = get_questions_collection()
    inserted = 0
    for q in QUESTIONS:
        if not col.find_one({"_id": q["_id"]}):
            col.insert_one(q)
            inserted += 1
    if inserted:
        print(f"✅ Auto-seeded {inserted} questions into the database.")
    else:
        print(f"✅ Question bank already populated ({len(QUESTIONS)} questions available).")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    _auto_seed()
    yield
    # ── Shutdown ──


app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description=(
        "A 1-Dimensional Adaptive Testing System that dynamically adjusts question "
        "difficulty using a simplified IRT model and generates AI-powered study plans."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, assets)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API routers
app.include_router(session_router, tags=["Session"])
app.include_router(question_router, tags=["Questions"])
app.include_router(analytics_router)



@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the AdaptIQ frontend SPA."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "message": "Adaptive Diagnostic Engine is running 🚀 — no frontend found."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "message": "Adaptive Diagnostic Engine is running 🚀"}

