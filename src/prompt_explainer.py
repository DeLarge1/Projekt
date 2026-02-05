from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


ROLE_HINTS = ["you are", "act as", "pretend to be", "as a"]
CONSTRAINT_HINTS = [
    "must",
    "only",
    "never",
    "do not",
    "without",
    "under",
    "in less than",
    "exactly",
]

OUTPUT_CONTROL_HINTS = [
    "creative",
    "best",
    "good",
    "improve",
    "interesting",
    "etc",
    "anything",
]


@dataclass
class PromptExplanation:
    why_it_works: List[str]
    why_it_might_fail: List[str]
    implicit_instructions: List[str]
    control_risks: List[str]


def _split_sentences(text: str) -> List[str]:
    chunks = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    return chunks if chunks else [text.strip()]


def explain_prompt(prompt: str) -> PromptExplanation:
    sentences = _split_sentences(prompt.lower())

    why_it_works: List[str] = []
    why_it_might_fail: List[str] = []
    implicit: List[str] = []
    risks: List[str] = []

    if any(any(h in s for h in ROLE_HINTS) for s in sentences):
        why_it_works.append("Prompt defines a role, which narrows behavior.")
        implicit.append("Model is expected to emulate a persona or profession.")
    else:
        why_it_might_fail.append("No explicit role/context, so output style can drift.")

    if any(any(h in s for h in CONSTRAINT_HINTS) for s in sentences):
        why_it_works.append("Prompt includes constraints, improving predictability.")
    else:
        why_it_might_fail.append("Missing hard constraints (format/length/scope).")

    if "example" in prompt.lower():
        why_it_works.append("Contains examples that anchor expected output.")
    else:
        why_it_might_fail.append("No examples provided, so formatting may vary.")

    if re.search(r"\bjson\b|\btable\b|\bbullets?\b", prompt.lower()):
        implicit.append("Output format is partially specified.")
    else:
        risks.append("Output format is underspecified.")

    if any(h in prompt.lower() for h in OUTPUT_CONTROL_HINTS):
        risks.append("Contains vague quality terms that are subjective.")

    if len(prompt.split()) < 12:
        why_it_might_fail.append("Prompt is very short; important assumptions are unstated.")

    if not risks:
        risks.append("No major control risk detected by heuristics.")

    return PromptExplanation(
        why_it_works=why_it_works,
        why_it_might_fail=why_it_might_fail,
        implicit_instructions=implicit,
        control_risks=risks,
    )
