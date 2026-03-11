# AI-Driven Adaptive Diagnostic Engine

A **1-Dimensional Adaptive Testing System** that dynamically adjusts question difficulty based on a student's responses, estimates their ability score, and generates a personalised AI study plan using OpenAI.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [API Documentation](#api-documentation)
4. [Adaptive Algorithm](#adaptive-algorithm)
5. [AI Integration Log](#ai-integration-log)

---

## Project Overview

The system simulates a GRE-style adaptive test:

- Starts every session at **ability = 0.5**.
- Selects the question whose difficulty is **closest to the current ability score**.
- After each answer, the ability score is updated up or down by **0.1**.
- Runs for exactly **10 questions**, then generates an AI-powered study plan.

Session data (ability score, question history, topics missed) is persisted in **MongoDB Atlas**.

---

## Setup Instructions

### 1 — Clone / navigate to the project

```bash
cd "adaptive-diagnostic-engine"
```

### 2 — Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure environment variables

Copy `.env` and fill in your credentials:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
OPENAI_API_KEY=sk-...
DATABASE_NAME=adaptive_diagnostic
```

### 5 — Seed the question bank

```bash
python scripts/seed_questions.py
```

### 6 — Start the server

```bash
uvicorn app.main:app --reload
```

The interactive API docs are available at **http://127.0.0.1:8000/docs**.

---

## API Documentation

### `POST /start-session`
Creates a new test session and returns the first question.

**Response**
```json
{
  "session_id": "abc-123",
  "first_question": {
    "question_id": "q5",
    "question_text": "...",
    "options": ["A", "B", "C", "D"],
    "difficulty": 0.5,
    "topic": "Algebra",
    "tags": ["linear equations"]
  }
}
```

---

### `GET /next-question/{session_id}`
Returns the next recommended question for the session.

---

### `POST /submit-answer`
Submits an answer, updates ability score, and returns the next question.

**Request**
```json
{
  "session_id": "abc-123",
  "question_id": "q5",
  "answer": "4"
}
```

**Response**
```json
{
  "correct": true,
  "ability_score": 0.6,
  "next_question": { "..." },
  "message": ""
}
```

---

### `POST /generate-study-plan/{session_id}`
Calls OpenAI to generate a personalised 3-step study plan based on session results.

**Response**
```json
{
  "study_plan": "1. Review probability...\n2. Practice vocabulary...\n3. Solve mixed problems..."
}
```

---

## Adaptive Algorithm

### Ability Update (Simplified IRT)

| Event | Formula |
|---|---|
| Correct answer | `ability = ability + 0.1` |
| Incorrect answer | `ability = ability - 0.1` |
| Clamp | `0.1 ≤ ability ≤ 1.0` |

### Question Selection

1. **Exclude** already-answered questions.
2. **Find** the question with difficulty closest to `current_ability`.
3. **Prefer** the same topic as the previous question (tie-breaking bonus of `0.001`).

This ensures *logical difficulty progression* — the test gets harder after correct answers and easier after incorrect ones, reflecting real adaptive testing systems like GRE and GMAT.

---

## AI Integration Log

### Tools Used
- **OpenAI GPT-3.5 Turbo** via the `openai` Python SDK.

### Prompt Design
Each prompt includes:
- Final ability score (0.1–1.0 scale)
- Accuracy percentage (correct / total)
- List of weak topics (topics where answers were incorrect)
- A directive to produce a **3-step, actionable study plan**

The system prompt establishes the model as a *GRE tutor and academic coach* to bias outputs toward structured, educationally sound advice.

### What the AI Handles Well
- Generating topic-specific, actionable recommendations
- Adapting tone based on accuracy (struggling students get more foundational steps)

### Known Limitations / What AI Couldn't Solve
- AI cannot access the actual question text or student's specific wrong answers — only topic-level metadata is passed.
- The AI may occasionally produce generic advice when all topics were answered correctly.
- OpenAI API latency (~1–3 s) means the study plan is not instant.

---

## Project Architecture

```
adaptive-diagnostic-engine/
│
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── database.py          ← MongoDB connection manager
│   ├── models.py            ← Pydantic request / response models
│   ├── adaptive_engine.py   ← IRT ability updates + question selection
│   ├── ai_service.py        ← OpenAI study plan generation
│   └── routes/
│       ├── session_routes.py   ← /start-session, /generate-study-plan
│       └── question_routes.py  ← /next-question, /submit-answer
│
├── scripts/
│   └── seed_questions.py    ← Populates MongoDB with 25 GRE questions
│
├── requirements.txt
├── .env
└── README.md
```
