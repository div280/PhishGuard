/* ─────────────────────────────────────────────────────
   PhishGuard – Analyzer Dashboard JavaScript
   ───────────────────────────────────────────────────── */

'use strict';

// ── Sample Messages ──────────────────────────────────
const SAMPLES = {
  phishing: `Dear Customer,

We have detected UNUSUAL ACTIVITY on your account!! Your account will be SUSPENDED immediately unless you verify your account now.

CLICK HERE to confirm your identity: http://secure-verify-account.com/login

This is URGENT!! Immediate action required to avoid account termination.

Password reset required within 24 hours or your bank account will be blocked.

Account Security Team`,

  spam: `CONGRATULATIONS!!! You have been selected as our LUCKY WINNER!!!

You've WON $50,000 in our FREE money lottery!! Claim your prize NOW before it EXPIRES!!!

Click now to claim your FREE gift: http://bit.ly/win-free-money

LIMITED OFFER - ACT NOW!! No credit card required! 100% FREE!!!
This offer expires SOON! Don't miss out on this AMAZING opportunity!!!

Winner Selection Team`,

  professional: `Dear Mr. Johnson,

I hope this message finds you well. I am writing to follow up on our discussion from last Thursday regarding the Q3 marketing proposal.

As requested, I have attached the revised budget breakdown and the updated timeline for your review. Please find the detailed analysis enclosed with this message.

Kindly let me know if you require any additional information or if you would like to schedule a call to discuss the next steps.

I look forward to hearing from you at your earliest convenience.

Best regards,
Sarah Mitchell
Senior Marketing Manager`,
};

// ── DOM Refs ──────────────────────────────────────────
const textarea       = document.getElementById('messageInput');
const charCount      = document.getElementById('charCount');
const analyzeBtn     = document.getElementById('analyzeBtn');
const clearBtn       = document.getElementById('clearBtn');
const loadingState   = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const errorToast     = document.getElementById('errorToast');
const errorMsg       = document.getElementById('errorMsg');

// ── Char Counter ──────────────────────────────────────
textarea.addEventListener('input', () => {
  const len = textarea.value.length;
  charCount.textContent = len.toLocaleString();
  charCount.style.color = len > 9000 ? 'var(--danger)' : len > 7000 ? 'var(--warning)' : 'var(--primary-g)';
});

// ── Clear ─────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  textarea.value = '';
  charCount.textContent = '0';
  charCount.style.color = '';
  resultsSection.style.display = 'none';
  loadingState.style.display   = 'none';
  textarea.focus();
});

// ── Sample Buttons ────────────────────────────────────
document.querySelectorAll('.sample-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const key = btn.dataset.sample;
    textarea.value = SAMPLES[key] || '';
    charCount.textContent = textarea.value.length.toLocaleString();
    textarea.focus();
    textarea.scrollTop = 0;
  });
});

// ── Analyze Again ─────────────────────────────────────
const analyzeAgainBtn = document.getElementById('analyzeAgainBtn');
if (analyzeAgainBtn) {
  analyzeAgainBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
    textarea.focus();
  });
}

// ── Toast ─────────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = msg;
  errorToast.classList.add('show');
  setTimeout(() => errorToast.classList.remove('show'), 4000);
}

// ── Loading Steps Animation ───────────────────────────
const LOADING_STEPS = [
  'Scanning for phishing patterns…',
  'Evaluating tone & sentiment…',
  'Computing clarity score…',
  'Detecting intent signals…',
  'Rating professionalism…',
  'Generating rewrite suggestion…',
];

function animateLoadingSteps() {
  const container = document.getElementById('loadingSteps');
  container.innerHTML = '';
  LOADING_STEPS.forEach((text, i) => {
    const el = document.createElement('div');
    el.className = 'loading-step';
    el.innerHTML = `<span class="step-dot"></span>${text}`;
    container.appendChild(el);
    setTimeout(() => el.classList.add('active'), i * 320);
  });
}

// ── Score Ring Animation ──────────────────────────────
function animateRing(id, score, color) {
  const fill = document.getElementById(id);
  if (!fill) return;
  const circumference = 226;
  const offset = circumference - (score / 100) * circumference;
  fill.style.stroke = color;
  setTimeout(() => { fill.style.strokeDashoffset = offset; }, 100);
}

// ── Progress Bar Animation ────────────────────────────
function animateBar(id, score) {
  const bar = document.getElementById(id);
  if (!bar) return;
  setTimeout(() => { bar.style.width = score + '%'; }, 100);
}

// ── Counter Animation ─────────────────────────────────
function animateNum(el, target, duration = 1200, suffix = '') {
  if (!el) return;
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = Math.floor(start) + suffix;
    if (start >= target) clearInterval(timer);
  }, 16);
}

// ── Color Helpers ─────────────────────────────────────
function scoreColor(score, inverted = false) {
  if (inverted) {
    // High score = bad (spam, danger)
    if (score >= 70) return '#FF4444';
    if (score >= 40) return '#FF8C00';
    return '#22C55E';
  } else {
    // High score = good (clarity, professionalism)
    if (score >= 80) return '#22C55E';
    if (score >= 50) return '#FF8C00';
    return '#FF4444';
  }
}

function badgeClass(riskLevel) {
  const r = (riskLevel || '').toLowerCase();
  if (r.includes('high') || r.includes('danger')) return 'badge-danger';
  if (r.includes('medium') || r.includes('caution')) return 'badge-warning';
  return 'badge-success';
}

function barClass(score, inverted = false) {
  const bad = inverted ? score >= 70 : score < 50;
  const mid = inverted ? score >= 40 : score < 70;
  if (bad) return inverted ? 'danger' : 'danger';
  if (mid) return 'warning';
  return 'success';
}

function toneEmoji(tone) {
  const map = {
    professional: '💼', friendly: '😊', neutral: '😐',
    aggressive: '⚡', suspicious: '🎭', promotional: '📣',
  };
  return map[(tone || '').toLowerCase()] || '📧';
}

function toneColor(tone) {
  const map = {
    professional: '#22C55E', friendly: '#38BDF8', neutral: '#8888AA',
    aggressive: '#FF4444', suspicious: '#FF8C00', promotional: '#A78BFA',
  };
  return map[(tone || '').toLowerCase()] || '#8888AA';
}

function intentEmoji(intent) {
  const map = {
    phishing: '🎣', scam: '⚠️', promotional: '📣',
    urgent: '🚨', transactional: '💳', professional: '💼',
    personal: '💬', 'general communication': '📧',
  };
  return map[(intent || '').toLowerCase()] || '📧';
}

// ── Render Results ────────────────────────────────────
function renderResults(data) {
  const { spam, tone, clarity, intent, professionalism, rewrite } = data;

  // ── Overall Risk Badge ──
  const overallRiskEl = document.getElementById('overallRisk');
  const riskText = spam.risk_level || 'Unknown';
  const riskCls  = badgeClass(riskText);
  overallRiskEl.className = `overall-risk-badge ${riskCls}`;
  overallRiskEl.innerHTML = `<span>${riskText === 'High Risk' ? '🔴' : riskText === 'Medium Risk' ? '🟠' : '🟢'}</span> ${riskText}`;

  // ── SPAM Card ──
  const spamColor = scoreColor(spam.score, true);
  document.getElementById('spamScoreNum').textContent = spam.score + '%';
  document.getElementById('spamScoreNum').style.color = spamColor;
  animateBar('spamBar', spam.score);
  document.getElementById('spamBar').className = `progress-bar ${barClass(spam.score, true)}`;
  document.getElementById('spamRiskBadge').className = `badge ${badgeClass(spam.risk_level)}`;
  document.getElementById('spamRiskBadge').textContent = spam.risk_level;

  const reasonsEl = document.getElementById('spamReasons');
  reasonsEl.innerHTML = spam.reasons.map(r => {
    const isOk = r.toLowerCase().includes('no major');
    return `<div class="spam-reason-item">
      <span class="reason-dot ${isOk ? 'reason-dot-ok' : 'reason-dot-danger'}"></span>
      <span>${r}</span>
    </div>`;
  }).join('');

  const kwEl = document.getElementById('spamKeywords');
  if (spam.suspicious_keywords && spam.suspicious_keywords.length > 0) {
    document.getElementById('keywordsRow').style.display = 'block';
    kwEl.innerHTML = spam.suspicious_keywords.map(kw => `<span class="kw-pill">${kw}</span>`).join('');
  } else {
    document.getElementById('keywordsRow').style.display = 'none';
  }

  // ── TONE Card ──
  const tc = toneColor(tone.dominant_tone);
  document.getElementById('toneEmoji').textContent = toneEmoji(tone.dominant_tone);
  const toneNameEl = document.getElementById('toneName');
  toneNameEl.textContent = tone.dominant_tone;
  toneNameEl.style.color = tc;
  document.getElementById('toneDesc').textContent = tone.description;

  const sentLabel = tone.sentiment_label || 'Neutral';
  const sentCls   = sentLabel === 'Positive' ? 'badge-success' : sentLabel === 'Negative' ? 'badge-danger' : 'badge-muted';
  document.getElementById('sentimentBadge').className = `badge ${sentCls}`;
  document.getElementById('sentimentBadge').textContent = `${sentLabel} (${tone.sentiment_compound})`;

  // ── INTENT Card ──
  document.getElementById('intentIcon').textContent = intent.icon || intentEmoji(intent.primary_intent);
  document.getElementById('intentName').textContent = intent.primary_intent;
  const intRiskCls = intent.risk_level === 'Dangerous' ? 'badge-danger' : intent.risk_level === 'Caution' ? 'badge-warning' : 'badge-success';
  document.getElementById('intentRisk').className = `badge ${intRiskCls}`;
  document.getElementById('intentRisk').textContent = intent.risk_level;

  const secIntEl = document.getElementById('secondaryIntents');
  if (intent.secondary_intents && intent.secondary_intents.length > 0) {
    document.getElementById('secondaryIntentsWrap').style.display = 'block';
    secIntEl.innerHTML = intent.secondary_intents.map(i =>
      `<span class="badge badge-muted">${i}</span>`
    ).join('');
  } else {
    document.getElementById('secondaryIntentsWrap').style.display = 'none';
  }

  // ── CLARITY Card ──
  const clarColor = scoreColor(clarity.score);
  const clarNumEl = document.getElementById('clarityScoreNum');
  clarNumEl.style.color = clarColor;
  animateNum(clarNumEl, clarity.score, 1200, '');
  document.getElementById('clarityLabel').textContent = clarity.label;
  document.getElementById('clarityLabel').style.color = clarColor;
  animateBar('clarityBar', clarity.score);
  document.getElementById('clarityBar').className = `progress-bar ${barClass(clarity.score)}`;

  const clarIssuesEl = document.getElementById('clarityIssues');
  clarIssuesEl.innerHTML = clarity.issues.map(issue =>
    `<div class="score-issue-item"><span style="color:var(--muted);font-size:0.9rem">•</span> ${issue}</div>`
  ).join('');

  const s = clarity.stats || {};
  document.getElementById('statWords').textContent  = s.word_count ?? '–';
  document.getElementById('statSents').textContent  = s.sentence_count ?? '–';
  document.getElementById('statAvgW').textContent   = s.avg_words_per_sentence ?? '–';
  document.getElementById('statAvgWl').textContent  = s.avg_word_length ?? '–';

  // ── PROFESSIONALISM Card ──
  const profColor = scoreColor(professionalism.score);
  const profNumEl = document.getElementById('profScoreNum');
  profNumEl.style.color = profColor;
  animateNum(profNumEl, professionalism.score, 1200, '');
  document.getElementById('profLabel').textContent = professionalism.rating;
  document.getElementById('profLabel').style.color = profColor;
  animateBar('profBar', professionalism.score);
  document.getElementById('profBar').className = `progress-bar ${barClass(professionalism.score)}`;

  const profNotesEl = document.getElementById('profNotes');
  profNotesEl.innerHTML = professionalism.notes.map(n =>
    `<div class="score-issue-item"><span style="color:var(--muted);font-size:0.9rem">•</span> ${n}</div>`
  ).join('');

  // ── REWRITE Card ──
  const rewriteCard = document.getElementById('rewriteCard');
  const rewriteContent = document.getElementById('rewriteContent');

  if (rewrite.needed && rewrite.suggestion) {
    rewriteCard.classList.remove('not-needed');
    const tags = (rewrite.improvements || []).map(imp =>
      `<span class="badge badge-primary">${imp}</span>`
    ).join('');
    rewriteContent.innerHTML = `
      <p class="rewrite-reason">${rewrite.reason}</p>
      <div class="improvement-tags">${tags}</div>
      <div class="rewrite-text-box" id="rewriteText">${escapeHtml(rewrite.suggestion)}</div>
      <div class="rewrite-actions">
        <button class="copy-btn" id="copyRewriteBtn">📋 Copy Rewrite</button>
      </div>`;
    document.getElementById('copyRewriteBtn').addEventListener('click', () => {
      navigator.clipboard.writeText(rewrite.suggestion).then(() => {
        document.getElementById('copyRewriteBtn').textContent = '✅ Copied!';
        setTimeout(() => { document.getElementById('copyRewriteBtn').textContent = '📋 Copy Rewrite'; }, 2000);
      });
    });
  } else {
    rewriteCard.classList.add('not-needed');
    rewriteContent.innerHTML = `
      <div class="no-rewrite">
        <span class="no-rewrite-icon">✅</span>
        <div class="no-rewrite-text">
          <strong>Looking good!</strong><br>
          ${rewrite.reason || 'Your message already meets quality standards.'}
        </div>
      </div>`;
  }

  // ── Show Results ──
  resultsSection.style.display = 'block';
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Staggered card animation
  document.querySelectorAll('.result-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
      card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, i * 120);
  });
}

// ── HTML Escape ───────────────────────────────────────
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ── Main Analyze Handler ──────────────────────────────
analyzeBtn.addEventListener('click', runAnalysis);
textarea.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runAnalysis();
});

async function runAnalysis() {
  const text = textarea.value.trim();
  if (!text) {
    showError('Please paste or type a message to analyze.');
    textarea.focus();
    return;
  }
  if (text.length < 10) {
    showError('Message is too short. Please enter at least 10 characters.');
    return;
  }

  // UI: enter loading state
  resultsSection.style.display = 'none';
  loadingState.style.display   = 'flex';
  analyzeBtn.disabled          = true;
  analyzeBtn.innerHTML         = '<span class="spinner" style="width:18px;height:18px;border-width:2px;"></span> Analyzing…';
  animateLoadingSteps();

  try {
    const resp = await fetch('/api/analyze', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ text }),
    });

    let data;
    try {
      data = await resp.json();
    } catch (e) {
      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status} status. Please check backend logs.`);
      }
      throw new Error('Failed to parse response from server.');
    }

    if (!resp.ok) {
      throw new Error(data.error || 'Analysis failed. Please try again.');
    }

    loadingState.style.display = 'none';
    renderResults(data);

  } catch (err) {
    loadingState.style.display = 'none';
    showError(err.message || 'Something went wrong. Please try again.');
  } finally {
    analyzeBtn.disabled  = false;
    analyzeBtn.innerHTML = '🔍 Analyze Message';
  }
}
