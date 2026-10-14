import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.study_quiz import StudyQuiz

TEXT = "Forests protect soil. Evaporation turns liquid water into water vapour."
QUESTIONS = [
    {"type": "multiple_choice", "question": "What do forests protect?", "options": ["Soil", "Ocean currents", "Volcanoes"], "answer": 0, "explanation": "The material states that forests protect soil.", "evidence_id": 0},
    {"type": "true_false", "question": "Evaporation changes liquid water into water vapour.", "options": ["True", "False"], "answer": 0, "explanation": "This is the change described in the material.", "evidence_id": 1},
]


def response(questions):
    return httpx.Response(200, json={"status": "completed", "usage": {"input_tokens": 20, "output_tokens": 30},
        "output": [{"content": [{"type": "output_text", "text": json.dumps({"questions": questions})}]}]},
        request=httpx.Request("POST", "https://api.openai.com/v1/responses"))


def test_grounded_mixed_quiz_and_disabled_mode(monkeypatch):
    calls = []
    def post(self, url, **kwargs):
        calls.append(kwargs["json"]); return response(QUESTIONS)
    monkeypatch.setattr(httpx.Client, "post", post)
    provider = StudyQuiz(Settings(api_key="mock"))
    quiz, usage = provider.generate(TEXT, True)
    assert quiz["kind"] == "ai" and len(quiz["questions"]) == 2
    assert usage["model_calls"] == 1 and usage["output_tokens"] == 30
    assert calls[0]["store"] is False
    assert json.loads(calls[0]["input"])["sentences"][0]["text"] == "Forests protect soil."
    assert quiz["questions"][1]["evidence"] == "Evaporation turns liquid water into water vapour."
    unavailable, usage = provider.generate(TEXT, False)
    assert unavailable["questions"] == [] and usage["model_calls"] == 0 and len(calls) == 1


@pytest.mark.parametrize("bad", [
    QUESTIONS[:1], QUESTIONS * 3,
    [QUESTIONS[0], {**QUESTIONS[1], "evidence_id": 99}],
    [QUESTIONS[0], {**QUESTIONS[1], "answer": 2}],
    [QUESTIONS[0], {**QUESTIONS[1], "answer": True}],
    [QUESTIONS[0], {**QUESTIONS[1], "options": ["Yes", "No"]}],
    [QUESTIONS[0], {**QUESTIONS[0], "question": "Another multiple choice question"}],
])
def test_invalid_or_unsupported_quiz_is_not_shown(monkeypatch, bad):
    monkeypatch.setattr(httpx.Client, "post", lambda *a, **k: response(bad))
    quiz, usage = StudyQuiz(Settings(api_key="mock")).generate(TEXT, True)
    assert quiz["kind"] == "unavailable" and quiz["questions"] == [] and quiz["warning"]
    assert usage["input_tokens"] == 20


def test_quiz_failure_preserves_safe_message(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("secret-key student-private-answer")
    monkeypatch.setattr(httpx.Client, "post", fail)
    quiz, usage = StudyQuiz(Settings(api_key="mock")).generate(TEXT, True)
    assert quiz["questions"] == [] and usage["unaccounted_calls"]
    assert "secret-key" not in quiz["warning"] and "student-private-answer" not in quiz["warning"]


def test_quiz_endpoint_cache_and_analysis_opt_in(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "quiz.db", api_key="mock", online=False))
    calls = []
    def generate(text, enabled=False):
        calls.append(enabled)
        return {"kind": "ai" if enabled else "unavailable", "questions": [dict(q, id=f"q{i}") for i, q in enumerate(QUESTIONS)] if enabled else [], "warning": None}, {"model_calls": int(enabled), "input_tokens": 20 if enabled else 0, "output_tokens": 30 if enabled else 0}
    monkeypatch.setattr(app.state.study_quiz, "generate", generate)
    monkeypatch.setattr(app.state.ai, "extract", lambda text: ([], {"model_calls": 1, "input_tokens": 0, "output_tokens": 0}, None))
    with TestClient(app) as client:
        body = {"text": TEXT, "session_id": "quiz-session"}
        first = client.post("/api/study-quiz", json=body).json()
        second = client.post("/api/study-quiz", json=body).json()
        assert first["usage"]["model_calls"] == 1 and second["usage"]["cache_hit"]
        assert calls == [True]
        guide = client.post("/api/analyze", json={**body, "generate_quiz": True, "use_ai": True}).json()
        assert guide["study_quiz"]["kind"] == "ai" and guide["usage"]["model_calls"] == 2
        assert "target_recommendations" not in guide
        explore = client.post("/api/analyze", json={**body, "generate_quiz": False, "use_ai": True}).json()
        assert explore["study_quiz"]["questions"] == [] and explore["usage"]["model_calls"] == 1
