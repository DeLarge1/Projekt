from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List


LOW_EFFORT_PATTERNS = {
    "idk",
    "i dont know",
    "i don't know",
    "n/a",
    "none",
    "nothing",
    "asdf",
    "ok",
    "no",
    "yes",
    "-",
}

CONTRADICTION_PAIRS = [
    ("always", "never"),
    ("like", "hate"),
    ("agree", "disagree"),
    ("easy", "difficult"),
    ("safe", "dangerous"),
]


@dataclass
class QualityResult:
    row_id: int
    text: str
    score: float
    flags: List[str]


class StudyResponseQualityChecker:
    """Hybrid text quality checker using simple heuristics + pairwise similarity."""

    def __init__(
        self,
        min_tokens: int = 6,
        max_similarity: float = 0.92,
        repetition_threshold: float = 0.45,
    ) -> None:
        self.min_tokens = min_tokens
        self.max_similarity = max_similarity
        self.repetition_threshold = repetition_threshold

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-zA-Z']+", text.lower())

    def _is_low_effort(self, text: str) -> bool:
        normalized = self._normalize_text(text)
        tokens = self._tokenize(normalized)
        if not tokens:
            return True
        if normalized in LOW_EFFORT_PATTERNS:
            return True
        if len(tokens) < self.min_tokens:
            return True

        unique_ratio = len(set(tokens)) / max(len(tokens), 1)
        if unique_ratio < self.repetition_threshold:
            return True

        return False

    def _has_internal_contradiction(self, text: str) -> bool:
        lowered = text.lower()
        return any(a in lowered and b in lowered for a, b in CONTRADICTION_PAIRS)

    def _copy_paste_flags(self, texts: Iterable[str]) -> List[bool]:
        text_list = list(texts)
        flags = [False for _ in text_list]

        for i in range(len(text_list)):
            for j in range(i + 1, len(text_list)):
                score = SequenceMatcher(None, text_list[i].lower(), text_list[j].lower()).ratio()
                if score >= self.max_similarity:
                    flags[i] = True
                    flags[j] = True
        return flags

    def score_responses(self, texts: Iterable[str]) -> List[QualityResult]:
        text_list = [str(t) for t in texts]
        copy_flags = self._copy_paste_flags(text_list)
        results: List[QualityResult] = []

        for idx, text in enumerate(text_list):
            flags: List[str] = []
            score = 100.0

            if self._is_low_effort(text):
                flags.append("low_effort")
                score -= 45

            if copy_flags[idx]:
                flags.append("possible_copy_paste")
                score -= 30

            if self._has_internal_contradiction(text):
                flags.append("possible_contradiction")
                score -= 25

            score = max(0.0, round(score, 2))
            results.append(QualityResult(row_id=idx, text=text, score=score, flags=flags))

        return results


def analyze_csv(input_path: Path, text_column: str, output_path: Path) -> List[Dict[str, str]]:
    with input_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("Input CSV has no rows.")

    if text_column not in rows[0]:
        raise ValueError(f"Column '{text_column}' not found. Available: {list(rows[0].keys())}")

    checker = StudyResponseQualityChecker()
    results = checker.score_responses(row.get(text_column, "") for row in rows)

    for row, result in zip(rows, results):
        row["quality_score"] = str(result.score)
        row["flags"] = "|".join(result.flags) if result.flags else ""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return rows
