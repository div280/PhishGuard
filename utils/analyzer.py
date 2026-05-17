"""
PhishGuard Analysis Engine
Lightweight local NLP using TextBlob, VADER, regex, and heuristics.
"""

import re
import string
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ──────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────

SPAM_KEYWORDS = [
    "urgent", "click now", "verify account", "verify your account",
    "password reset", "bank alert", "crypto", "free money", "winner",
    "lottery", "limited offer", "account suspended", "immediate action required",
    "act now", "claim your prize", "you have been selected", "congratulations",
    "guaranteed", "risk free", "risk-free", "no obligation", "winner selected",
    "dear customer", "dear user", "dear valued", "update your information",
    "confirm your identity", "suspicious activity", "unusual activity",
    "verify now", "click here", "click the link", "sign in now",
    "log in now", "your account will be", "will be suspended",
    "will be terminated", "will be deactivated", "validate your",
    "free gift", "you won", "you've won", "you have won",
    "earn money", "make money fast", "work from home", "bitcoin",
    "investment opportunity", "double your", "100% free", "absolutely free",
    "no credit card", "limited time", "expires soon", "last chance",
    "final notice", "payment required", "overdue", "invoice attached",
    "wire transfer", "western union", "moneygram", "gift card",
    "itunes", "google play card", "buy gift card",
]

PHISHING_PATTERNS = [
    r"https?://[^\s]+",                           # any URL
    r"\b(?:paypal|amazon|apple|microsoft|google|netflix|bank)\b",
    r"\bsocial\s*security\b",
    r"\bcredit\s*card\b",
    r"\bssn\b",
    r"\bpassword\b",
    r"\bpin\b",
    r"\baccount\s*number\b",
    r"\brouting\s*number\b",
    r"\bverif(?:y|ication)\b",
    r"\bsuspend(?:ed|ension)?\b",
    r"\bblock(?:ed)?\b",
    r"\bunauthorized\b",
    r"\bhack(?:ed|ing)?\b",
    r"\bscam\b",
    r"\bfraud\b",
    r"\billegal\b",
    r"\bconfirm\s*your\b",
]

TONE_KEYWORDS = {
    "aggressive":    ["immediately", "now!", "demand", "must", "required", "failure", "consequences", "legal action", "lawsuit", "police", "report", "threat"],
    "promotional":   ["buy", "sale", "discount", "offer", "deal", "save", "promo", "free", "gift", "bonus", "percent off", "% off", "bargain"],
    "professional":  ["regards", "sincerely", "please", "kindly", "thank you", "appreciate", "ensure", "inform", "request", "attached", "enclosed"],
    "friendly":      ["hi", "hey", "hope", "hope you", "looking forward", "catch up", "nice", "great", "wonderful", "happy", "enjoy"],
    "suspicious":    SPAM_KEYWORDS[:20],
}

INTENT_RULES = {
    "phishing":      ["verify account", "confirm identity", "click here", "click the link", "update your information", "password", "suspended", "unusual activity"],
    "scam":          ["lottery", "winner", "prize", "free money", "crypto", "bitcoin", "investment", "wire transfer", "gift card"],
    "promotional":   ["sale", "discount", "offer", "deal", "free", "promo", "limited time", "buy now"],
    "urgent":        ["urgent", "immediately", "act now", "last chance", "expires", "final notice", "overdue"],
    "transactional": ["invoice", "payment", "receipt", "order", "shipped", "delivery", "confirm", "transaction"],
    "professional":  ["regards", "sincerely", "dear", "attached", "please find", "as per", "pursuant", "kindly"],
    "personal":      ["hi", "hey", "how are you", "how's", "miss you", "talk soon", "catch up", "family", "friend"],
}

VADER = SentimentIntensityAnalyzer()


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _lower(text: str) -> str:
    return text.lower()


def _word_count(text: str) -> int:
    return len(text.split())


def _sentence_count(text: str) -> int:
    sentences = re.split(r'[.!?]+', text.strip())
    return max(1, len([s for s in sentences if s.strip()]))


def _avg_word_length(text: str) -> float:
    words = [w for w in text.split() if w.isalpha()]
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def _caps_ratio(text: str) -> float:
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return 0.0
    return sum(1 for c in alpha if c.isupper()) / len(alpha)


def _exclamation_count(text: str) -> int:
    return text.count('!')


def _url_count(text: str) -> int:
    return len(re.findall(r"https?://[^\s]+", text))


def _count_keyword_hits(text: str, keywords: list) -> list:
    found = []
    lt = _lower(text)
    for kw in keywords:
        if kw.lower() in lt:
            found.append(kw)
    return found


# ──────────────────────────────────────────────────────────────
# SPAM SCORE
# ──────────────────────────────────────────────────────────────

def analyze_spam(text: str) -> dict:
    score = 0
    reasons = []
    lt = _lower(text)

    # Keyword hits
    hits = _count_keyword_hits(text, SPAM_KEYWORDS)
    kw_score = min(50, len(hits) * 8)
    score += kw_score
    if hits:
        reasons.append(f"Suspicious phrases detected: {', '.join(hits[:5])}")

    # ALL CAPS abuse
    cr = _caps_ratio(text)
    if cr > 0.5:
        score += 20
        reasons.append("Excessive use of capital letters")
    elif cr > 0.3:
        score += 10
        reasons.append("High proportion of capital letters")

    # Excessive punctuation
    exc = _exclamation_count(text)
    if exc >= 5:
        score += 15
        reasons.append(f"Excessive exclamation marks ({exc})")
    elif exc >= 3:
        score += 8
        reasons.append(f"Multiple exclamation marks ({exc})")

    # URLs
    urls = _url_count(text)
    if urls >= 3:
        score += 15
        reasons.append(f"Multiple suspicious links ({urls})")
    elif urls == 2:
        score += 8
        reasons.append(f"Links detected ({urls})")
    elif urls == 1:
        score += 4
        reasons.append("External link detected")

    # Phishing patterns via regex
    phish_hits = []
    for pat in PHISHING_PATTERNS:
        if re.search(pat, lt):
            phish_hits.append(pat)
    ph_score = min(20, len(phish_hits) * 4)
    score += ph_score
    if phish_hits and len(phish_hits) > 2:
        reasons.append("Multiple phishing-related patterns detected")

    score = min(100, score)

    if score >= 70:
        risk = "High Risk"
    elif score >= 40:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    if not reasons:
        reasons.append("No major spam indicators detected")

    return {
        "score": score,
        "risk_level": risk,
        "reasons": reasons,
        "suspicious_keywords": hits[:10],
    }


# ──────────────────────────────────────────────────────────────
# TONE ANALYSIS
# ──────────────────────────────────────────────────────────────

def analyze_tone(text: str) -> dict:
    vader_scores = VADER.polarity_scores(text)
    compound = vader_scores["compound"]

    scores = {}
    lt = _lower(text)

    for tone, keywords in TONE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw.lower() in lt)
        scores[tone] = hits

    # Boost tones based on VADER compound
    if compound >= 0.3:
        scores["friendly"] = scores.get("friendly", 0) + 2
        scores["professional"] = scores.get("professional", 0) + 1
    elif compound <= -0.3:
        scores["aggressive"] = scores.get("aggressive", 0) + 2
        scores["suspicious"] = scores.get("suspicious", 0) + 1

    # Exclamation boost
    exc = _exclamation_count(text)
    if exc >= 3:
        scores["promotional"] = scores.get("promotional", 0) + 2
        scores["aggressive"] = scores.get("aggressive", 0) + 1

    # Caps boost
    if _caps_ratio(text) > 0.4:
        scores["aggressive"] = scores.get("aggressive", 0) + 2

    # Determine dominant tone
    dominant = max(scores, key=lambda k: scores[k]) if any(v > 0 for v in scores.values()) else "neutral"

    if all(v == 0 for v in scores.values()):
        dominant = "Neutral"
    else:
        dominant = dominant.capitalize()

    tone_descriptions = {
        "Professional": "The message has a formal and business-like tone.",
        "Friendly":     "The message comes across as warm and approachable.",
        "Neutral":      "The message tone is balanced and objective.",
        "Aggressive":   "The message uses demanding or threatening language.",
        "Suspicious":   "The message contains suspicious or manipulative language patterns.",
        "Promotional":  "The message reads as a marketing or promotional communication.",
    }

    return {
        "dominant_tone": dominant,
        "sentiment_compound": round(compound, 3),
        "sentiment_label": "Positive" if compound >= 0.05 else "Negative" if compound <= -0.05 else "Neutral",
        "description": tone_descriptions.get(dominant, "Unable to determine specific tone."),
        "tone_scores": {k: v for k, v in scores.items()},
    }


# ──────────────────────────────────────────────────────────────
# CLARITY SCORE
# ──────────────────────────────────────────────────────────────

def analyze_clarity(text: str) -> dict:
    score = 100
    issues = []

    word_count = _word_count(text)
    sent_count = _sentence_count(text)
    avg_words_per_sent = word_count / sent_count if sent_count else word_count
    avg_wl = _avg_word_length(text)

    # Very short message
    if word_count < 5:
        score -= 30
        issues.append("Message is too short to evaluate properly")

    # Long sentences
    if avg_words_per_sent > 35:
        score -= 25
        issues.append("Sentences are too long — difficult to read")
    elif avg_words_per_sent > 25:
        score -= 15
        issues.append("Sentences are somewhat long")

    # Long average word length (complex vocabulary)
    if avg_wl > 8:
        score -= 15
        issues.append("Complex vocabulary detected — consider simpler words")
    elif avg_wl > 6.5:
        score -= 8
        issues.append("Some complex words detected")

    # Excessive repetition
    words = [w.lower().strip(string.punctuation) for w in text.split() if len(w) > 4]
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1
    repeated = [w for w, c in word_freq.items() if c >= 4]
    if repeated:
        score -= min(20, len(repeated) * 5)
        issues.append(f"Repeated words detected: {', '.join(repeated[:4])}")

    # Excessive punctuation
    exc = _exclamation_count(text)
    if exc >= 5:
        score -= 15
        issues.append("Excessive exclamation marks hurt clarity")
    elif exc >= 3:
        score -= 8

    # Grammar check via TextBlob (simple heuristic)
    blob = TextBlob(text)
    if len(blob.sentences) == 0:
        score -= 10
        issues.append("No recognizable sentences found")

    # ALL CAPS
    if _caps_ratio(text) > 0.4:
        score -= 10
        issues.append("ALL CAPS text reduces readability")

    score = max(0, min(100, score))

    if score >= 80:
        label = "Excellent"
    elif score >= 60:
        label = "Good"
    elif score >= 40:
        label = "Fair"
    else:
        label = "Poor"

    if not issues:
        issues.append("Message is clear and well-structured")

    return {
        "score": score,
        "label": label,
        "issues": issues,
        "stats": {
            "word_count": word_count,
            "sentence_count": sent_count,
            "avg_words_per_sentence": round(avg_words_per_sent, 1),
            "avg_word_length": round(avg_wl, 1),
        },
    }


# ──────────────────────────────────────────────────────────────
# INTENT DETECTION
# ──────────────────────────────────────────────────────────────

def analyze_intent(text: str) -> dict:
    lt = _lower(text)
    intent_scores = {}

    for intent, keywords in INTENT_RULES.items():
        hits = sum(1 for kw in keywords if kw.lower() in lt)
        intent_scores[intent] = hits

    # VADER boost for urgency
    vader = VADER.polarity_scores(text)
    if vader["compound"] <= -0.3:
        intent_scores["urgent"] = intent_scores.get("urgent", 0) + 1

    if all(v == 0 for v in intent_scores.values()):
        primary_intent = "General Communication"
        secondary = []
    else:
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent = sorted_intents[0][0].capitalize()
        secondary = [i[0].capitalize() for i in sorted_intents[1:3] if i[1] > 0]

    intent_icons = {
        "Phishing": "🎣",
        "Scam": "⚠️",
        "Promotional": "📣",
        "Urgent": "🚨",
        "Transactional": "💳",
        "Professional": "💼",
        "Personal": "💬",
        "General communication": "📧",
    }

    danger_intents = {"Phishing", "Scam", "Urgent"}
    risk_level = "Dangerous" if primary_intent in danger_intents else \
                 "Caution" if "Promotional" in [primary_intent] + secondary else "Safe"

    return {
        "primary_intent": primary_intent,
        "secondary_intents": secondary,
        "icon": intent_icons.get(primary_intent, "📧"),
        "risk_level": risk_level,
        "intent_scores": intent_scores,
    }


# ──────────────────────────────────────────────────────────────
# PROFESSIONALISM RATING
# ──────────────────────────────────────────────────────────────

def analyze_professionalism(text: str) -> dict:
    score = 70  # start neutral
    notes = []

    lt = _lower(text)

    # Positive signals
    prof_signals = ["regards", "sincerely", "dear", "please", "kindly", "thank you",
                    "appreciate", "attached", "enclosed", "as requested", "pursuant",
                    "looking forward", "please find", "inform you"]
    for sig in prof_signals:
        if sig in lt:
            score = min(100, score + 5)

    # Negative signals
    if _caps_ratio(text) > 0.4:
        score -= 20
        notes.append("Excessive capitalization is unprofessional")

    if _exclamation_count(text) >= 4:
        score -= 15
        notes.append("Too many exclamation marks reduce professionalism")

    slang = ["lol", "omg", "wtf", "bruh", "gonna", "wanna", "gotta", "ya'll",
             "nope", "yep", "sup", "dunno", "kinda", "sorta"]
    slang_found = [s for s in slang if re.search(r'\b' + s + r'\b', lt)]
    if slang_found:
        score -= min(20, len(slang_found) * 5)
        notes.append(f"Informal/slang language detected: {', '.join(slang_found)}")

    spam_hits = _count_keyword_hits(text, SPAM_KEYWORDS)
    if spam_hits:
        score -= min(25, len(spam_hits) * 5)
        notes.append("Spam-like language lowers professionalism")

    # Grammar via TextBlob
    blob = TextBlob(text)
    if len(blob.sentences) < 1:
        score -= 10
        notes.append("Poor sentence structure detected")

    score = max(0, min(100, score))

    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Fair"
    else:
        rating = "Poor"

    if not notes:
        notes.append("Message meets professional communication standards")

    return {
        "score": score,
        "rating": rating,
        "notes": notes,
    }


# ──────────────────────────────────────────────────────────────
# REWRITE SUGGESTION
# ──────────────────────────────────────────────────────────────

def generate_rewrite(text: str, spam_score: int, clarity_score: int, tone: str, prof_score: int) -> dict:
    needs_rewrite = spam_score >= 40 or clarity_score < 60 or prof_score < 60 or tone in ["Aggressive", "Suspicious"]

    if not needs_rewrite:
        return {
            "needed": False,
            "suggestion": None,
            "reason": "Your message already meets quality standards. No rewrite needed.",
        }

    # Build a professional template rewrite
    blob = TextBlob(text)
    sentences = [str(s).strip() for s in blob.sentences if str(s).strip()]

    # Clean sentences: remove spam keywords, normalize punctuation
    cleaned = []
    for sent in sentences:
        # Remove excessive exclamations
        sent = re.sub(r'!+', '.', sent)
        # Remove ALL CAPS words (replace with title case)
        sent = re.sub(r'\b([A-Z]{3,})\b', lambda m: m.group(0).title(), sent)
        # Remove URLs
        sent = re.sub(r'https?://[^\s]+', '[link]', sent)
        # Strip leading/trailing whitespace
        sent = sent.strip()
        if sent and len(sent) > 3:
            cleaned.append(sent)

    # Replace spam phrases with professional alternatives
    replacements = {
        "click now":                "please visit the provided link",
        "click here":               "please refer to the attachment",
        "verify account":           "verify your information",
        "verify your account":      "verify your account details",
        "urgent":                   "time-sensitive",
        "immediately":              "at your earliest convenience",
        "act now":                  "please respond at your earliest convenience",
        "free money":               "a complimentary benefit",
        "winner":                   "selected recipient",
        "limited offer":            "time-limited opportunity",
        "account suspended":        "account requires attention",
        "immediate action required":"your prompt attention is appreciated",
        "password reset":           "credential update",
        "bank alert":               "account notification",
        "crypto":                   "digital assets",
        "lottery":                  "selection process",
    }

    rewrite_text = " ".join(cleaned) if cleaned else text
    rw_lower = rewrite_text.lower()
    for phrase, replacement in replacements.items():
        rw_lower = rw_lower.replace(phrase, replacement)

    # Re-capitalize first letter of each sentence
    sentences_out = re.split(r'(?<=[.!?])\s+', rw_lower)
    sentences_out = [s[:1].upper() + s[1:] if s else s for s in sentences_out]
    rewrite_text = " ".join(sentences_out)

    # Add professional salutation/closing if missing
    has_greeting = any(rewrite_text.lower().startswith(g) for g in ["dear", "hello", "hi ", "good"])
    has_closing = any(c in rewrite_text.lower() for c in ["regards", "sincerely", "thank you", "best"])

    if not has_greeting:
        rewrite_text = "Dear Recipient,\n\n" + rewrite_text
    if not has_closing:
        rewrite_text = rewrite_text.rstrip(".") + "\n\nKind regards."

    reasons = []
    if spam_score >= 40:
        reasons.append("High spam score reduced")
    if clarity_score < 60:
        reasons.append("Clarity improved")
    if prof_score < 60:
        reasons.append("Professionalism enhanced")
    if tone in ["Aggressive", "Suspicious"]:
        reasons.append("Tone neutralized")

    return {
        "needed": True,
        "suggestion": rewrite_text,
        "reason": "Rewrite applied: " + " | ".join(reasons),
        "improvements": reasons,
    }


# ──────────────────────────────────────────────────────────────
# MASTER ANALYSIS FUNCTION
# ──────────────────────────────────────────────────────────────

def analyze_message(text: str) -> dict:
    text = text.strip()
    if not text:
        return {"error": "No text provided for analysis."}

    spam      = analyze_spam(text)
    tone      = analyze_tone(text)
    clarity   = analyze_clarity(text)
    intent    = analyze_intent(text)
    prof      = analyze_professionalism(text)
    rewrite   = generate_rewrite(
        text,
        spam_score=spam["score"],
        clarity_score=clarity["score"],
        tone=tone["dominant_tone"],
        prof_score=prof["score"],
    )

    return {
        "spam":           spam,
        "tone":           tone,
        "clarity":        clarity,
        "intent":         intent,
        "professionalism": prof,
        "rewrite":        rewrite,
    }
