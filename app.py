"""Flask web application for AI Registration Assistant."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session

from chatbot import RegistrationAssistant

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-key-change-in-production")
assistant = RegistrationAssistant(BASE_DIR)


def current_session_id() -> str:
    if "chat_session_id" not in session:
        session["chat_session_id"] = uuid.uuid4().hex
    return session["chat_session_id"]


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", ""))
    result = assistant.respond(message, current_session_id())
    return jsonify(result)


@app.post("/api/reset")
def reset():
    assistant.reset_session(current_session_id())
    return jsonify({"ok": True, "message": "Conversation reset."})


@app.get("/admin")
def admin():
    return render_template("admin.html", analytics=assistant.analytics())


@app.get("/api/analytics")
def analytics():
    return jsonify(assistant.analytics())


@app.get("/health")
def health():
    return jsonify({"status": "ok", "task_id": "AI-SS-001"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
