# Project Report: AI Registration Assistant

**Task ID:** AI-SS-001  
**Student Name:** Abhinav Singh  
**Student Code:** DAS002971  
**Technology:** Python, NLTK, scikit-learn, Flask, HTML, CSS, JavaScript, JSON

## 1. Introduction

The AI Registration Assistant is a conversational student-support system designed to guide users through internship registration. The project solves a common problem: registration pages can be confusing, while a chatbot can collect information step by step, answer frequently asked questions, validate entries, and provide immediate confirmation.

## 2. Objectives

The objectives were to implement NLP preprocessing, intent recognition, entity extraction, dialog management, validation, local data storage, and a usable web interface. The project also includes bonus features: FAQ handling, English/Hindi-Hinglish support, sentiment analysis, conversation logging, and an admin dashboard.

## 3. System Design

The solution uses a hybrid architecture. General questions are handled by a machine-learning intent classifier trained from phrases in `intents.json`. Text is normalized using NLTK Snowball stemming. TF-IDF converts words and bigrams into numeric features, and Logistic Regression predicts the most likely intent with a confidence score.

A deterministic state machine manages registration. Its states are name, email, program, year, experience, confirmation, and completion. This prevents the general classifier from misinterpreting answers during form collection. Regular expressions extract email and name entities. Validation functions reject invalid names, email formats, years, and experience levels.

## 4. Implementation

The backend is written in Python. Flask exposes the chatbot page, chat API, reset API, analytics API, health endpoint, and admin dashboard. Browser sessions receive independent conversation IDs. Registration records and chat logs are stored in JSON files, meeting the no-database requirement.

The responsive frontend uses HTML, CSS, and JavaScript. It displays chat bubbles, quick FAQ actions, a registration progress bar, validation messages, and conversation reset controls. The dashboard displays total registrations, message counts, intent distribution, sentiment totals, and recent applications.

## 5. Testing and Results

Automated pytest cases verify greeting classification, entity extraction, invalid-email handling, FAQ response, and the complete registration workflow. Manual tests cover unknown questions, cancellation, restarting, confirmation, mobile layout, and admin analytics. The chatbot successfully stores a validated registration and generates a unique registration ID.

## 6. Limitations and Future Scope

The ML model uses a small custom training set and is suitable for a demonstration rather than a production service. Future improvements could include a larger multilingual dataset, spaCy named-entity recognition, transformer-based intent classification, encrypted storage, authentication for the admin dashboard, email verification, cloud deployment, and a production database.

## 7. Conclusion

The project meets the required objectives by combining NLP, machine learning, entity extraction, validation, dialog management, registration confirmation, and web integration. The hybrid approach is simple to explain, reliable for structured registration, and easy to extend with additional intents or fields.
