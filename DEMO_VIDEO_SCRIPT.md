# YouTube Demo Video Script

**Suggested title:** AI Registration Assistant - DAS002971 | Python NLP Chatbot Internship Project

## 1. Introduction (20-30 seconds)

Hello, my name is Abhinav Singh, and my student code is DAS002971. This is my AI Registration Assistant project for Task AI-SS-001. It is built using Python, NLTK, scikit-learn, Flask, HTML, CSS, JavaScript, and JSON.

## 2. Explain the Interface (30 seconds)

Show the homepage. Explain the feature cards, chatbot window, quick-action buttons, progress bar, input box, and reset button. Mention that it is responsive and requires no database.

## 3. Demonstrate FAQs (30-45 seconds)

Ask: “Who can apply?”, “Is it free?”, and “How do I submit the task?” Explain that a TF-IDF plus Logistic Regression model recognizes these intents.

## 4. Demonstrate Registration (1-2 minutes)

Type the following:

1. Register me
2. Abhinav Singh
3. Enter an invalid email first to show validation
4. abhinav@example.com
5. BTech AI Engineering
6. 2
7. Intermediate
8. YES

Show the generated registration ID and progress reaching 100%.

## 5. Show Admin Dashboard (30-45 seconds)

Open `/admin`. Show registration totals, message totals, intent distribution, sentiment counts, and the recent registrations table.

## 6. Code Walkthrough (1-2 minutes)

Show:

- `data/intents.json`: patterns and responses
- `chatbot.py`: NLP model, entity extraction, validators, dialog states, JSON storage
- `app.py`: Flask routes
- `templates` and `static`: interface files
- `tests/test_chatbot.py`: automated tests

Run `pytest -q` and show that all tests pass.

## 7. Closing (15 seconds)

This project meets the core requirements and includes bonus features such as multilingual support, FAQ handling, sentiment analysis, logging, an admin dashboard, and a Flask web interface. Thank you.
