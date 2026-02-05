from __future__ import annotations

import argparse
import json
from pathlib import Path

from prompt_explainer import explain_prompt
from quality_checker import analyze_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Study Toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    quality_cmd = sub.add_parser("quality-check", help="Score responses in CSV file")
    quality_cmd.add_argument("--input", required=True, type=Path, help="Input CSV path")
    quality_cmd.add_argument("--text-column", required=True, help="Name of text column")
    quality_cmd.add_argument("--output", required=True, type=Path, help="Output CSV path")

    explain_cmd = sub.add_parser("explain-prompt", help="Explain a prompt")
    explain_cmd.add_argument("--prompt", required=True, help="Prompt text")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "quality-check":
        df = analyze_csv(args.input, args.text_column, args.output)
        print(f"Saved {len(df)} rows to {args.output}")

    if args.command == "explain-prompt":
        result = explain_prompt(args.prompt)
        print(
            json.dumps(
                {
                    "why_it_works": result.why_it_works,
                    "why_it_might_fail": result.why_it_might_fail,
                    "implicit_instructions": result.implicit_instructions,
                    "control_risks": result.control_risks,
                },
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
