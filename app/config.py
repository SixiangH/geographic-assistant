from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


@dataclass
class Settings:
    database: Path = ROOT / ".runtime" / "knowledge.sqlite3"
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    online: bool = os.getenv("ONLINE_LOOKUP_ENABLED", "true").lower() == "true"
    input_price: str = os.getenv("INPUT_PRICE_PER_MILLION", "")
    output_price: str = os.getenv("OUTPUT_PRICE_PER_MILLION", "")


settings = Settings()
