from pathlib import Path

from src.prompt_explainer import explain_prompt
from src.quality_checker import StudyResponseQualityChecker, analyze_csv


def test_quality_checker_flags_expected_issues() -> None:
    checker = StudyResponseQualityChecker()
    texts = [
        "idk",
        "I always like this and I never like this product.",
        "This answer has enough details and is unique in content.",
        "This answer has enough details and is unique in content.",
    ]

    results = checker.score_responses(texts)

    assert "low_effort" in results[0].flags
    assert "possible_contradiction" in results[1].flags
    assert "possible_copy_paste" in results[2].flags
    assert "possible_copy_paste" in results[3].flags


def test_analyze_csv_outputs_score_columns(tmp_path: Path) -> None:
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("id,response\n1,idk\n2,Good detailed answer here\n", encoding="utf-8")

    output_csv = tmp_path / "out.csv"
    rows = analyze_csv(input_csv, "response", output_csv)

    assert "quality_score" in rows[0]
    assert "flags" in rows[0]
    assert output_csv.exists()


def test_prompt_explainer_produces_sections() -> None:
    explanation = explain_prompt(
        "You are a financial analyst. Must return JSON. Provide one example."
    )

    assert explanation.why_it_works
    assert isinstance(explanation.control_risks, list)
