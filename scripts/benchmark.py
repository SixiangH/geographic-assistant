"""Measure local recognition latency / 测量本地识别延迟. No paid model calls / 不调用付费模型."""
import json
import math
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.main import create_app


def main():
    words = (ROOT / "data" / "sample.txt").read_text(encoding="utf-8").split()
    text = " ".join((words * 20)[:2000])
    with tempfile.TemporaryDirectory() as directory:
        app = create_app(Settings(database=Path(directory) / "benchmark.db", api_key="", online=False))
        with TestClient(app) as client:
            durations = []
            for index in range(30):
                started = time.perf_counter()
                response = client.post("/api/analyze", json={"text": text, "session_id": f"benchmark-{index}"})
                response.raise_for_status()
                assert not response.json()["usage"]["cache_hit"]
                durations.append((time.perf_counter() - started) * 1000)
            ordered = sorted(durations)
            result = {"runs": 30, "words": 2000, "mode": "local", "p95_ms": round(ordered[math.ceil(.95 * len(ordered)) - 1], 2), "mean_ms": round(sum(durations) / len(durations), 2), "model_calls": 0}
            card_durations = []
            for _ in range(30):
                started = time.perf_counter()
                client.get("/api/card?id=wiki:Oceanic%20climate").raise_for_status()
                card_durations.append((time.perf_counter() - started) * 1000)
            result["local_card_p95_ms"] = round(sorted(card_durations)[28], 2)
    out = ROOT / "test-results"
    out.mkdir(exist_ok=True)
    (out / "benchmark.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
