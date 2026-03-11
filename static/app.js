/* ═══════════════════════════════════════════════════
   AdaptIQ — Frontend Application Logic
   Handles: API calls, screen transitions, mini-chart,
            ability display, study plan rendering
═══════════════════════════════════════════════════ */

'use strict';

// ── State ──────────────────────────────────────────
const state = {
  sessionId: null,
  currentQuestion: null,
  questionNumber: 0,
  abilityScore: 0.5,
  answeredThisRound: false,
  diffProgression: [],   // difficulty of each served question
  correctCount: 0,
  totalAnswered: 0,
};

// ── Helpers ────────────────────────────────────────
function $(id) { return document.getElementById(id); }

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  $(id).classList.add('active');
}

function showToast(msg, duration = 3000) {
  const t = $('toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => t.classList.add('hidden'), duration);
}

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    return data;
  } catch (err) {
    showToast('⚠️ ' + err.message);
    throw err;
  }
}

// ── Letter labels ──────────────────────────────────
const LETTERS = ['A', 'B', 'C', 'D'];

// ── Mini difficulty-progression chart ─────────────
function drawMiniChart() {
  const canvas = $('diff-chart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const pts = state.diffProgression;
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  if (pts.length < 2) return;

  // Grid line at 0.5
  ctx.strokeStyle = 'rgba(255,255,255,.06)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  const mid = H - (0.5 / 1.0) * H;
  ctx.moveTo(0, mid); ctx.lineTo(W, mid);
  ctx.stroke();

  // Gradient fill
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, 'rgba(99,102,241,.35)');
  grad.addColorStop(1, 'rgba(99,102,241,.0)');

  const step = W / (pts.length - 1);

  ctx.beginPath();
  ctx.moveTo(0, H - (pts[0] / 1.0) * H);
  for (let i = 1; i < pts.length; i++) {
    const x = i * step;
    const y = H - (pts[i] / 1.0) * H;
    ctx.lineTo(x, y);
  }
  // Fill area
  ctx.lineTo((pts.length - 1) * step, H);
  ctx.lineTo(0, H);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.moveTo(0, H - (pts[0] / 1.0) * H);
  for (let i = 1; i < pts.length; i++) {
    ctx.lineTo(i * step, H - (pts[i] / 1.0) * H);
  }
  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 2;
  ctx.lineJoin = 'round';
  ctx.stroke();

  // Dots
  for (let i = 0; i < pts.length; i++) {
    ctx.beginPath();
    ctx.arc(i * step, H - (pts[i] / 1.0) * H, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#818cf8';
    ctx.fill();
  }
}

// ── Render question ────────────────────────────────
function renderQuestion(q) {
  state.currentQuestion = q;
  state.answeredThisRound = false;

  // Meta
  $('q-topic').textContent = q.topic;
  $('q-diff-badge').textContent = `Difficulty: ${q.difficulty.toFixed(1)}`;

  // Difficulty fill bar
  $('diff-bar').style.width = (q.difficulty * 100) + '%';

  // Text
  $('question-text').textContent = q.question_text;

  // Options
  const grid = $('options-grid');
  grid.innerHTML = '';
  q.options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.id = `opt-${i}`;
    btn.innerHTML = `<span class="option-letter">${LETTERS[i]}</span><span>${opt}</span>`;
    btn.onclick = () => submitAnswer(opt, i);
    grid.appendChild(btn);
  });

  // Hide feedback & next
  $('feedback-box').classList.add('hidden');
  $('feedback-box').className = 'feedback-box hidden';
  $('next-btn-wrap').classList.add('hidden');

  // Progress
  const progressPct = (state.questionNumber / 10) * 100;
  $('progress-bar').style.width = Math.max(10, progressPct) + '%';
  $('q-number').textContent = state.questionNumber;

  // Ability display
  $('ability-display').textContent = state.abilityScore.toFixed(2);

  // Chart
  drawMiniChart();

  // Animate card re-entry
  const card = document.querySelector('.question-card');
  card.style.animation = 'none';
  void card.offsetHeight; // reflow
  card.style.animation = 'card-in .4s cubic-bezier(.4,0,.2,1)';
}

// ── Start session ─────────────────────────────────
async function startSession() {
  const btn = $('btn-start');
  btn.disabled = true;
  btn.innerHTML = `<span>Starting…</span>`;

  try {
    const data = await apiFetch('/start-session', { method: 'POST' });
    state.sessionId = data.session_id;
    state.questionNumber = 1;
    state.abilityScore = 0.5;
    state.diffProgression = [data.first_question.difficulty];
    state.correctCount = 0;
    state.totalAnswered = 0;

    showScreen('screen-question');
    renderQuestion(data.first_question);
  } catch (_) {
    btn.disabled = false;
    btn.innerHTML = `<span>Begin Assessment</span>
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
  }
}

// ── Submit answer ─────────────────────────────────
async function submitAnswer(answer, optIndex) {
  if (state.answeredThisRound) return;
  state.answeredThisRound = true;

  // Disable all options
  document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);

  try {
    const data = await apiFetch('/submit-answer', {
      method: 'POST',
      body: JSON.stringify({
        session_id: state.sessionId,
        question_id: state.currentQuestion.question_id,
        answer: answer,
      }),
    });

    state.totalAnswered++;
    state.abilityScore = data.ability_score;
    if (data.correct) state.correctCount++;

    // Highlight chosen option
    const chosenBtn = $(`opt-${optIndex}`);
    chosenBtn.classList.add(data.correct ? 'correct' : 'incorrect');

    // If wrong, highlight the correct one
    if (!data.correct) {
      const correctAnswer = state.currentQuestion.options.find(
        (_, i) => state.currentQuestion.options[i] === state.currentQuestion.correct_answer
      );
      // Find and highlight correct index
      state.currentQuestion.options.forEach((opt, i) => {
        if (opt === state.currentQuestion.correct_answer) {
          $(`opt-${i}`).classList.add('correct');
        }
      });
    }

    // Feedback
    const fb = $('feedback-box');
    fb.classList.remove('hidden', 'correct-fb', 'incorrect-fb');
    if (data.correct) {
      fb.classList.add('correct-fb');
      fb.innerHTML = `<span>✅</span><span>Correct! Difficulty will increase slightly.</span>`;
    } else {
      fb.classList.add('incorrect-fb');
      fb.innerHTML = `<span>❌</span><span>Incorrect. The next question will be a bit easier.</span>`;
    }

    // Update ability display
    $('ability-display').textContent = data.ability_score.toFixed(2);

    // Show next button
    $('next-btn-wrap').classList.remove('hidden');
    const nextLabel = $('btn-next-label');

    if (data.next_question) {
      state._nextQuestion = data.next_question;
      state.diffProgression.push(data.next_question.difficulty);
      nextLabel.textContent = state.questionNumber >= 9 ? 'Final Question →' : 'Next Question';
    } else {
      // Test complete
      state._nextQuestion = null;
      nextLabel.textContent = 'See Results';
    }

  } catch (_) {
    state.answeredThisRound = false;
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = false);
  }
}

// ── Next question / results ────────────────────────
async function nextQuestion() {
  if (state._nextQuestion) {
    state.questionNumber++;
    renderQuestion(state._nextQuestion);
  } else {
    // Fetch study plan
    showScreen('screen-loading');
    try {
      const data = await apiFetch(`/generate-study-plan/${state.sessionId}`, { method: 'POST' });
      showResults(data.study_plan);
    } catch (_) {
      showResults('Unable to generate study plan. Please try again.');
    }
  }
}

// ── Show results ───────────────────────────────────
function showResults(studyPlan) {
  const accuracy = Math.round((state.correctCount / state.totalAnswered) * 100);
  const pct = ((state.abilityScore - 0.1) / 0.9) * 100;

  $('res-accuracy').textContent = `${state.correctCount}/${state.totalAnswered}`;
  $('res-ability').textContent = state.abilityScore.toFixed(2);

  // Color ability value based on level
  const abilityEl = $('res-ability');
  if (state.abilityScore < 0.45) abilityEl.style.color = '#34d399';
  else if (state.abilityScore < 0.7) abilityEl.style.color = '#f59e0b';
  else abilityEl.style.color = '#818cf8';

  // Meter
  setTimeout(() => {
    $('meter-fill').style.width = pct + '%';
    $('meter-thumb').style.left = pct + '%';
  }, 200);

  // Study plan — format it nicely
  const formatted = studyPlan
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
  $('study-plan-text').innerHTML = formatted;

  // Weak topics (from session progression inferred — show ability level)
  let label = 'Foundational';
  if (state.abilityScore >= 0.7) label = 'Advanced';
  else if (state.abilityScore >= 0.45) label = 'Intermediate';
  $('res-topics').textContent = label;

  showScreen('screen-results');
}

// ── Restart ────────────────────────────────────────
function restartTest() {
  // Reset state
  Object.assign(state, {
    sessionId: null,
    currentQuestion: null,
    questionNumber: 0,
    abilityScore: 0.5,
    answeredThisRound: false,
    diffProgression: [],
    correctCount: 0,
    totalAnswered: 0,
    _nextQuestion: null,
  });

  // Reset meter
  $('meter-fill').style.width = '50%';
  $('meter-thumb').style.left = '50%';

  // Reset start button
  $('btn-start').disabled = false;
  $('btn-start').innerHTML = `<span>Begin Assessment</span>
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;

  showScreen('screen-landing');
}
