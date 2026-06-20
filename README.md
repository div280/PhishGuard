# PhishGuard : AI-Powered Email & Message Quality Analyzer
### Detects phishing, spam, and toxic content in emails and messages using NLP-based analysis.

---

## Features

- **Spam Detection** - classifies unsolicited or bulk message patterns
- **Phishing Analysis** - flags suspicious links, sender patterns, and social engineering cues
- **Tone Detection** - identifies aggressive, urgent, or manipulative language
- **Clarity Score** - rates message readability and structure
- **Intent Detection** - determines whether a message is informational, promotional, or malicious
- **Professional Rewrite Suggestions** - rewrites flagged messages into clean, professional versions
- **Cybersecurity Dashboard UI** - modern, real-time analysis interface

---

## Tech Stack

- Python
- FastAPI
- HTML / CSS / JavaScript
- NLP-based Text Analysis (TextBlob)

---

## Project Preview

<img width="700" alt="image" src="https://github.com/user-attachments/assets/384d87f3-f95d-40f8-a4aa-e3ea26a07aed" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/664978ae-adc2-46dd-b03f-c3b386860812" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/026e89f3-913d-4f78-9dd9-5aac8d9b66a0" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/597bb814-0879-485d-a08d-a671c75d0a56" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/14035fa9-c8a7-48a8-afa5-41338f466c37" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/69e7ea6e-a2c7-499a-8f08-d5596e709fe5" />

---

## Installation

Clone the repository:
```bash
git clone https://github.com/div280/PhishGuard.git
```

Move into project folder:
```bash
cd PhishGuard
```

Create and activate virtual environment (Windows):
```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Download required NLP data:
```bash
python -m textblob.download_corpora
```

Run the application:
```bash
uvicorn main:app --reload
```

Open in browser: `http://127.0.0.1:8000`

---



