# AI Registration Assistant

**Task ID:** AI-SS-001  
**Student:** Abhinav Singh  
**Student Code:** DAS002971  
**Domain:** Student Support and Internship Management NLP

## Project Overview

AI Registration Assistant is a Flask-based conversational chatbot that guides students through internship registration. It combines an NLP intent-classification model with deterministic dialog management, regex entity extraction, validation, JSON storage, FAQ support, sentiment logging, and an admin dashboard.

## Main Features

- Machine-learning intent recognition using TF-IDF and Logistic Regression
- NLP preprocessing using NLTK Snowball stemming
- Entity extraction for name, email, and study year
- Multi-step registration workflow with context/state management
- Input validation and helpful fallback responses
- Registration confirmation with unique registration ID
- FAQ handling for eligibility, fees, skills, details, status, and submission
- Basic English/Hindi-Hinglish registration support
- Sentiment analysis and conversation logging
- Flask responsive web interface
- Admin analytics dashboard
- JSON storage, so no database is required
- Automated tests with pytest

## Project Structure

```text
AI_Registration_Assistant_DAS002971/
├── app.py
├── chatbot.py
├── requirements.txt
├── data/
│   ├── intents.json
│   ├── registrations.json
│   └── chat_logs.json
├── templates/
│   ├── index.html
│   └── admin.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── tests/test_chatbot.py
├── screenshots/
├── PROJECT_REPORT.pdf
├── PROJECT_REPORT.md
├── DEMO_VIDEO_SCRIPT.md
├── BLOG_POST.md
└── SUBMISSION_CHECKLIST.md
```

## Installation

1. Install Python 3.10 or later.
2. Open a terminal inside the project folder.
3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate it.

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Web Application

```bash
python app.py
```

Open these URLs:

- Chatbot: `http://127.0.0.1:5000`
- Admin dashboard: `http://127.0.0.1:5000/admin`
- Health endpoint: `http://127.0.0.1:5000/health`

## Example Registration Conversation

```text
User: Register me
Assistant: Please enter your full name.
User: Abhinav Singh
Assistant: Please enter your email address.
User: abhinav@example.com
Assistant: What degree or field are you studying?
User: BTech AI Engineering
Assistant: Which year of study are you in?
User: 2
Assistant: What is your programming experience?
User: Intermediate
Assistant: Reply YES to submit or NO to restart.
User: YES
Assistant: Registration completed successfully with a unique ID.
```

## Run Automated Tests

```bash
pytest -q
```

## NLP and Machine-Learning Approach

Each training phrase in `data/intents.json` receives an intent label. `TfidfVectorizer` converts text and bigrams into numerical features. `LogisticRegression` learns the relationship between those features and intent labels. During an active registration, a state machine takes priority over the classifier so that every answer is validated as the expected field.

## Storage

- Successful applications: `data/registrations.json`
- Conversation analytics: `data/chat_logs.json`

Do not commit real private student data to a public repository. The included files start empty.

## Task Link

Original task: `https://www.freeinternships.in/` (AI Registration Assistant, AI-SS-001)

## Submission

Upload this folder to a public GitHub repository, record a YouTube demonstration, create a blog post under **Task Submit**, and include screenshots, the project report, GitHub URL, and YouTube URL.
