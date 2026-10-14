import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


TEXT = "France has an oceanic climate and rainfall throughout the year."


def slot(session):
    key = hashlib.sha256((session + "TrueFalseFalse" + TEXT).encode()).hexdigest()
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % 64


def test_independent_students_do_not_serialize_model_requests(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "parallel.db", api_key="mock", online=False))
    barrier = threading.Barrier(2)
    def extract(text):
        barrier.wait(timeout=5)
        return [], {"model_calls": 1, "input_tokens": 1, "output_tokens": 1}, None
    monkeypatch.setattr(app.state.ai, "extract", extract)
    first, second = "student-one", "student-two"
    while slot(first) == slot(second):
        second += "x"
    with TestClient(app) as client, ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(client.post, "/api/analyze", json={"text": TEXT, "use_ai": True, "session_id": session}) for session in [first, second]]
        assert all(f.result(timeout=10).status_code == 200 for f in futures)


def test_duplicate_submission_shares_paid_result(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "duplicate.db", api_key="mock", online=False))
    calls = []
    def extract(text):
        calls.append(text)
        return [], {"model_calls": 1, "input_tokens": 1, "output_tokens": 1}, None
    monkeypatch.setattr(app.state.ai, "extract", extract)
    with TestClient(app) as client, ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(client.post, "/api/analyze", json={"text": TEXT, "use_ai": True, "session_id": "same-student"}) for _ in range(2)]
        results = [f.result(timeout=10).json() for f in futures]
        assert len(calls) == 1
        assert sorted(r["usage"]["model_calls"] for r in results) == [0, 1]
