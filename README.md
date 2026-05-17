# PhishGuard

AI-Powered Email & Message Quality Analyzer

## Features

- Spam Detection
- Phishing Analysis
- Tone Detection
- Clarity Score
- Intent Detection
- Professional Rewrite Suggestions
- Modern Cybersecurity Dashboard UI

---

## Tech Stack

- Python
- FastAPI
- HTML/CSS/JavaScript
- NLP-based Text Analysis

---

## Installation

Clone the repository:

```bash
git clone https://github.com/div280/PhishGuard.git

Move into project folder: cd PhishGuard

Create virtual environment:(Windows)
 python -m venv .venv
 .venv\Scripts\activate

Install dependencies:
 pip install -r requirements.txt

Download required NLP data:
 python -m textblob.download_corpora

Run the application:
 uvicorn main:app --reload