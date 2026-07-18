"""Core NLP and dialog-management logic for AI Registration Assistant.

Task: AI-SS-001
Student: Abhinav Singh (DAS002971)
"""
from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,59}$")


@dataclass
class ConversationSession:
    state: str = "idle"
    language: str = "en"
    user_data: dict[str, str] = field(default_factory=dict)


class JsonStore:
    """Tiny thread-safe JSON-list store used instead of a database."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def read_all(self) -> list[dict[str, Any]]:
        with self.lock:
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                return []

    def append(self, item: dict[str, Any]) -> None:
        with self.lock:
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    data = []
            except (json.JSONDecodeError, OSError):
                data = []
            data.append(item)
            self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class RegistrationAssistant:
    """Hybrid NLP assistant: ML intent classification + deterministic form flow."""

    FLOW = ["name", "email", "program", "year", "experience", "confirm"]
    POSITIVE_WORDS = {"good", "great", "excellent", "happy", "love", "helpful", "thanks", "thank"}
    NEGATIVE_WORDS = {"bad", "angry", "confused", "hate", "problem", "worried", "sad", "difficult"}

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.intents_path = self.data_dir / "intents.json"
        self.registrations = JsonStore(self.data_dir / "registrations.json")
        self.logs = JsonStore(self.data_dir / "chat_logs.json")
        self.sessions: dict[str, ConversationSession] = {}
        self.stemmer = SnowballStemmer("english")
        self.intents = self._load_intents()
        self.model = self._train_intent_model()

    def _load_intents(self) -> list[dict[str, Any]]:
        payload = json.loads(self.intents_path.read_text(encoding="utf-8"))
        return payload["intents"]

    def _normalize(self, text: str) -> str:
        tokens = re.findall(r"[a-zA-Z]+", text.lower())
        return " ".join(self.stemmer.stem(token) for token in tokens if token not in ENGLISH_STOP_WORDS)

    def _train_intent_model(self) -> Pipeline:
        texts: list[str] = []
        labels: list[str] = []
        for intent in self.intents:
            for pattern in intent["patterns"]:
                texts.append(pattern)
                labels.append(intent["tag"])
        model = Pipeline([
            ("tfidf", TfidfVectorizer(preprocessor=self._normalize, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ])
        model.fit(texts, labels)
        return model

    def classify_intent(self, text: str) -> tuple[str, float]:
        normalized = self._normalize(text)
        for intent in self.intents:
            for pattern in intent["patterns"]:
                if normalized and normalized == self._normalize(pattern):
                    return intent["tag"], 0.99
        probabilities = self.model.predict_proba([text])[0]
        classes = self.model.classes_
        index = int(probabilities.argmax())
        return str(classes[index]), float(probabilities[index])

    @staticmethod
    def extract_entities(text: str) -> dict[str, str]:
        entities: dict[str, str] = {}
        email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        if email:
            entities["email"] = email.group(0)
        name = re.search(r"(?:my name is|i am|i'm)\s+([A-Za-z][A-Za-z .'-]{1,59})", text, re.I)
        if name:
            candidate = re.split(r"\b(?:and|my email|studying|from)\b", name.group(1), maxsplit=1, flags=re.I)[0]
            entities["name"] = candidate.strip(" .")
        year = re.search(r"\b(?:year|semester)?\s*([1-4])(?:st|nd|rd|th)?\b", text, re.I)
        if year:
            entities["year"] = year.group(1)
        return entities

    @staticmethod
    def _detect_language(text: str) -> str:
        if re.search(r"[\u0900-\u097F]", text) or any(
            phrase in text.lower() for phrase in ["mujhe", "karna hai", "kaise", "registration karo", "madad"]
        ):
            return "hi"
        return "en"

    def sentiment(self, text: str) -> str:
        words = set(re.findall(r"[a-zA-Z]+", text.lower()))
        score = len(words & self.POSITIVE_WORDS) - len(words & self.NEGATIVE_WORDS)
        return "positive" if score > 0 else "negative" if score < 0 else "neutral"

    def _get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession()
        return self.sessions[session_id]

    def reset_session(self, session_id: str) -> None:
        self.sessions[session_id] = ConversationSession()

    @staticmethod
    def _clean_name(text: str) -> str:
        entities = RegistrationAssistant.extract_entities(text)
        return entities.get("name", text).strip().title()

    @staticmethod
    def _normalize_year(text: str) -> str | None:
        lower = text.lower().strip()
        mapping = {
            "first": "1", "1st": "1", "one": "1",
            "second": "2", "2nd": "2", "two": "2",
            "third": "3", "3rd": "3", "three": "3",
            "fourth": "4", "4th": "4", "four": "4", "final": "4",
        }
        for key, value in mapping.items():
            if re.search(rf"\b{re.escape(key)}\b", lower):
                return value
        match = re.search(r"\b([1-4])\b", lower)
        return match.group(1) if match else None

    @staticmethod
    def _normalize_experience(text: str) -> str | None:
        lower = text.lower()
        aliases = {
            "beginner": ["beginner", "new", "no experience", "basic", "fresher"],
            "intermediate": ["intermediate", "some experience", "medium", "1 year", "one year"],
            "advanced": ["advanced", "expert", "professional", "experienced", "2 years", "3 years"],
        }
        for level, words in aliases.items():
            if any(word in lower for word in words):
                return level.title()
        return None

    def _response_for_intent(self, tag: str) -> str:
        for intent in self.intents:
            if intent["tag"] == tag:
                return intent["responses"][0]
        return "I am not sure I understood. Please rephrase, or type 'help'."

    @staticmethod
    def _progress(state: str) -> int:
        mapping = {"idle": 0, "await_name": 10, "await_email": 30, "await_program": 50,
                   "await_year": 65, "await_experience": 80, "await_confirm": 95, "completed": 100}
        return mapping.get(state, 0)

    def _save_registration(self, session: ConversationSession) -> dict[str, Any]:
        registration_id = f"DAS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        record = {
            "registration_id": registration_id,
            "task_id": "AI-SS-001",
            "student_code": "DAS002971",
            **session.user_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "Registered",
        }
        self.registrations.append(record)
        return record

    def respond(self, message: str, session_id: str) -> dict[str, Any]:
        message = (message or "").strip()
        session = self._get_session(session_id)
        detected_language = self._detect_language(message)
        if session.state == "idle":
            session.language = detected_language

        if not message:
            reply = "Please type a message so I can help you."
            return self._pack(reply, "empty", 1.0, session, message)

        lower = message.lower()
        if lower in {"cancel", "stop registration", "restart", "reset"}:
            self.reset_session(session_id)
            session = self._get_session(session_id)
            reply = "Registration cancelled. Type 'register' when you want to begin again."
            return self._pack(reply, "cancel", 1.0, session, message)

        if lower in {"help", "madad", "मदद"} and session.state != "idle":
            reply = "You are currently completing registration. Reply to the current question, or type 'cancel' to stop."
            return self._pack(reply, "help", 1.0, session, message)

        # Deterministic dialog management while registration is active.
        if session.state == "await_name":
            name = self._clean_name(message)
            if not NAME_RE.fullmatch(name) or len(name.split()) < 2:
                reply = "Please enter your full name using letters, for example: Abhinav Singh."
                return self._pack(reply, "name_validation", 1.0, session, message)
            session.user_data["name"] = name
            session.state = "await_email"
            reply = f"Nice to meet you, {name}! Please enter your email address."
            return self._pack(reply, "name", 1.0, session, message)

        if session.state == "await_email":
            email = self.extract_entities(message).get("email", message.strip()).lower()
            if not EMAIL_RE.fullmatch(email):
                reply = "That email format is not valid. Please enter an address like name@example.com."
                return self._pack(reply, "email_validation", 1.0, session, message)
            session.user_data["email"] = email
            session.state = "await_program"
            reply = "Email verified. What degree or field are you studying? For example: BTech AI Engineering."
            return self._pack(reply, "email", 1.0, session, message)

        if session.state == "await_program":
            program = re.sub(r"\s+", " ", message).strip()
            if len(program) < 3 or len(program) > 80:
                reply = "Please enter a valid degree or field between 3 and 80 characters."
                return self._pack(reply, "program_validation", 1.0, session, message)
            session.user_data["program"] = program
            session.state = "await_year"
            reply = "Which year of study are you in? Enter 1, 2, 3, or 4."
            return self._pack(reply, "program", 1.0, session, message)

        if session.state == "await_year":
            year = self._normalize_year(message)
            if not year:
                reply = "Please enter a study year from 1 to 4."
                return self._pack(reply, "year_validation", 1.0, session, message)
            session.user_data["year"] = year
            session.state = "await_experience"
            reply = "What is your Python/programming experience: Beginner, Intermediate, or Advanced?"
            return self._pack(reply, "year", 1.0, session, message)

        if session.state == "await_experience":
            experience = self._normalize_experience(message)
            if not experience:
                reply = "Please choose Beginner, Intermediate, or Advanced."
                return self._pack(reply, "experience_validation", 1.0, session, message)
            session.user_data["experience"] = experience
            session.state = "await_confirm"
            data = session.user_data
            reply = (
                "Please confirm your details:\n"
                f"Name: {data['name']}\nEmail: {data['email']}\nProgram: {data['program']}\n"
                f"Year: {data['year']}\nExperience: {data['experience']}\n"
                "Reply YES to submit or NO to restart."
            )
            return self._pack(reply, "experience", 1.0, session, message)

        if session.state == "await_confirm":
            if lower in {"yes", "y", "confirm", "submit", "haan", "ha"}:
                record = self._save_registration(session)
                session.state = "completed"
                reply = (
                    "Registration completed successfully!\n"
                    f"Your registration ID is {record['registration_id']}.\n"
                    "Keep this ID for your records."
                )
                return self._pack(reply, "confirmation", 1.0, session, message, completed=True,
                                  registration_id=record["registration_id"])
            if lower in {"no", "n", "restart", "nahi"}:
                session.user_data = {}
                session.state = "await_name"
                reply = "No problem. Let us restart. Please enter your full name."
                return self._pack(reply, "restart", 1.0, session, message)
            reply = "Please reply YES to submit or NO to restart the registration."
            return self._pack(reply, "confirmation_validation", 1.0, session, message)

        if session.state == "completed" and lower in {"register", "register again", "new registration"}:
            session.user_data = {}
            session.state = "await_name"
            reply = "Starting a new registration. Please enter your full name."
            return self._pack(reply, "register", 1.0, session, message)

        # NLP classification for general conversation.
        intent, confidence = self.classify_intent(message)
        if intent == "register" or any(x in lower for x in ["registration karo", "apply karna", "रजिस्टर"]):
            session.user_data = {}
            session.state = "await_name"
            if session.language == "hi":
                reply = "ठीक है! रजिस्ट्रेशन शुरू करते हैं। कृपया अपना पूरा नाम लिखें।"
            else:
                reply = "Great! Let us start your registration. Please enter your full name."
            confidence = max(confidence, 0.95)
        elif confidence < 0.15:
            intent = "unknown"
            reply = "I am not sure I understood. Ask about registration, eligibility, fees, skills, submission, or type 'help'."
        else:
            reply = self._response_for_intent(intent)

        return self._pack(reply, intent, confidence, session, message)

    def _pack(self, reply: str, intent: str, confidence: float, session: ConversationSession,
              message: str, completed: bool = False, registration_id: str | None = None) -> dict[str, Any]:
        payload = {
            "reply": reply,
            "intent": intent,
            "confidence": round(confidence, 3),
            "state": session.state,
            "progress": self._progress(session.state),
            "sentiment": self.sentiment(message),
            "completed": completed,
            "registration_id": registration_id,
        }
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "intent": intent,
            "confidence": round(confidence, 3),
            "state": session.state,
            "sentiment": payload["sentiment"],
        })
        return payload

    def analytics(self) -> dict[str, Any]:
        registrations = self.registrations.read_all()
        logs = self.logs.read_all()
        intents: dict[str, int] = {}
        sentiments: dict[str, int] = {"positive": 0, "neutral": 0, "negative": 0}
        for log in logs:
            intents[log.get("intent", "unknown")] = intents.get(log.get("intent", "unknown"), 0) + 1
            sentiment = log.get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        return {
            "total_registrations": len(registrations),
            "total_messages": len(logs),
            "intent_counts": dict(sorted(intents.items(), key=lambda item: item[1], reverse=True)),
            "sentiment_counts": sentiments,
            "registrations": list(reversed(registrations[-50:])),
        }
