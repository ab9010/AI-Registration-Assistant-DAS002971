from pathlib import Path

from chatbot import RegistrationAssistant


def make_assistant(tmp_path: Path) -> RegistrationAssistant:
    source = Path(__file__).resolve().parents[1] / "data" / "intents.json"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "intents.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return RegistrationAssistant(tmp_path)


def test_intent_classifier_recognizes_greeting(tmp_path):
    bot = make_assistant(tmp_path)
    intent, confidence = bot.classify_intent("hello there")
    assert intent == "greeting"
    assert confidence > 0.2


def test_entity_extraction(tmp_path):
    bot = make_assistant(tmp_path)
    entities = bot.extract_entities("My name is Abhinav Singh and my email is abhi@example.com")
    assert entities["name"] == "Abhinav Singh"
    assert entities["email"] == "abhi@example.com"


def test_invalid_email_is_rejected(tmp_path):
    bot = make_assistant(tmp_path)
    sid = "test-user"
    bot.respond("register", sid)
    bot.respond("Abhinav Singh", sid)
    result = bot.respond("wrong-email", sid)
    assert result["state"] == "await_email"
    assert "not valid" in result["reply"]


def test_full_registration_flow(tmp_path):
    bot = make_assistant(tmp_path)
    sid = "full-flow"
    assert bot.respond("I want to register", sid)["state"] == "await_name"
    assert bot.respond("Abhinav Singh", sid)["state"] == "await_email"
    assert bot.respond("abhinav@example.com", sid)["state"] == "await_program"
    assert bot.respond("BTech AI Engineering", sid)["state"] == "await_year"
    assert bot.respond("2", sid)["state"] == "await_experience"
    assert bot.respond("Intermediate", sid)["state"] == "await_confirm"
    result = bot.respond("YES", sid)
    assert result["completed"] is True
    assert result["registration_id"].startswith("DAS-")
    assert len(bot.registrations.read_all()) == 1


def test_faq_response(tmp_path):
    bot = make_assistant(tmp_path)
    result = bot.respond("How do I submit the task?", "faq")
    assert result["intent"] == "submission"
    assert "GitHub" in result["reply"]
