from __future__ import annotations

import re
import unicodedata

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0
CATEGORIES = {"country", "place", "physical", "climate", "landform", "process", "concept", "human"}
AMBIGUITIES = {
    "Georgia": ["wiki:Georgia (country)", "wiki:Georgia (U.S. state)"],
    "Congo": ["wiki:Democratic Republic of the Congo", "wiki:Republic of the Congo", "wiki:Congo River"],
    "Amazon": ["wiki:Amazon River", "wiki:Amazon rainforest"],
}


def validate_text(text: str, records: list[dict]):
    if not text.strip():
        raise ValueError("Please paste an English passage or upload a UTF-8 .txt file.")
    if len(text.encode("utf-8")) > 1_000_000:
        raise ValueError("The material must be no larger than 1 MB.")
    if len(text.split()) > 10_000:
        raise ValueError("Please use a passage of 10,000 words or fewer.")
    if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
        raise ValueError("The material contains unsupported control characters. Please use plain text.")
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isascii() for c in letters) / len(letters) < 0.65:
        raise ValueError("Please use learning materials written primarily in English.")
    # Exact short geographical names remain valid despite language-detector uncertainty.
    if text.strip().casefold() in {a.casefold() for r in records for a in r["aliases"]}:
        return
    try:
        languages = detect_langs(text)
    except LangDetectException:
        raise ValueError("Please add a readable English passage.")
    if languages[0].lang != "en":
        raise ValueError("Please use learning materials written primarily in English. Add a full English sentence if the input is very short.")


def utf16_offset(text: str, position: int):
    return len(text[:position].encode("utf-16-le")) // 2


class Recognizer:
    def __init__(self, records: list[dict]):
        self.records = records
        aliases = {}
        for record in records:
            for alias in record["aliases"]:
                # Parenthetical article names are not generally prose aliases.
                aliases.setdefault(alias.casefold(), []).append(record)
        self.aliases = aliases
        terms = sorted(aliases, key=len, reverse=True)
        self.pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(t) for t in terms) + r")(?!\w)", re.IGNORECASE)

    def recognize(self, text: str):
        spans = []
        for m in self.pattern.finditer(text):
            candidates = self.aliases[m.group().casefold()]
            # Avoid common prose words and lower-case country/city collisions.
            if all(r["category"] in {"country", "place"} for r in candidates) and not m.group()[0].isupper():
                continue
            if m.group().casefold() == "us" and m.group() != "US":
                continue
            if m.group().casefold() == "plain" and not re.search(r"coastal|flood|alluvial|land|flat|grass|fertile", text[max(0,m.start()-60):m.end()+60], re.I):
                continue
            spans.append(self.mention(text, m.start(), m.end(), candidates))
        for term, identifiers in AMBIGUITIES.items():
            for match in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text):
                if any(match.start() < s["py_end"] and match.end() > s["py_start"] for s in spans):
                    continue
                candidates = [r for r in self.records if r["id"] in identifiers]
                if candidates:
                    spans.append(self.mention(text, match.start(), match.end(), candidates))
        return sorted(spans, key=lambda s: s["start"])

    @staticmethod
    def mention(text, start, end, candidates, kind="explicit", confidence=1.0):
        unique = {r["id"]: r for r in candidates}
        choices = [{"id": r["id"], "title": r["title"], "category": r["category"]} for r in unique.values()]
        resolved = len(choices) == 1
        return {"start": utf16_offset(text, start), "end": utf16_offset(text, end), "py_start": start, "py_end": end,
                "text": text[start:end], "id": choices[0]["id"] if resolved else None, "title": choices[0]["title"] if resolved else text[start:end],
                "category": choices[0]["category"] if resolved else "ambiguous", "kind": kind, "confidence": confidence, "candidates": choices if not resolved else []}

    def merge_ai(self, text, spans, discoveries):
        for item in discoveries[:80]:
            if not isinstance(item, dict):
                continue
            phrase = item.get("text", "")
            title = item.get("title", "")
            if not isinstance(title, str):
                continue
            title = title.strip()
            category = item.get("category")
            confidence = item.get("confidence", 0)
            if not isinstance(phrase, str) or not isinstance(confidence, (int, float)) or not 2 <= len(phrase) <= 250 or not 1 <= len(title) <= 120 or category not in CATEGORIES or not 0.8 <= confidence <= 1:
                continue
            candidates = self.aliases.get(title.casefold()) or [{"id": "remote:" + title, "title": title, "category": category}]
            for match in re.finditer(re.escape(phrase), text):
                if any(match.start() < s["py_end"] and match.end() > s["py_start"] for s in spans):
                    continue
                spans.append(self.mention(text, match.start(), match.end(), candidates, item.get("kind", "explicit"), confidence))
        return sorted(spans, key=lambda s: s["start"])
