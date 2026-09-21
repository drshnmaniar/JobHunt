from __future__ import annotations

import argparse
import os
from pathlib import Path

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assess a candidate's fit for a job description with TypeSafe."
    )
    parser.add_argument("job", help="Path to a job-description Markdown file")
    parser.add_argument(
        "--profile", default=str(ROOT / "candidate_profile.md"),
        help="Path to the candidate profile (default: candidate_profile.md)",
    )
    args = parser.parse_args()

    if not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit(
            "Set TYPESAFE_API_KEY before running. Example: "
            '$env:TYPESAFE_API_KEY = "your_key"'
        )

    state = {
        "candidate_profile": read_text(Path(args.profile)),
        "job_description": read_text(Path(args.job)),
    }
    questions = {
        "fit_score": Score(
            instructions=(
                "Assess the candidate's overall fit for `job_description` using only "
                "evidence in `candidate_profile`. Consider demonstrated responsibilities, "
                "domain knowledge, seniority, and required skills."
            ),
            criteria=[
                "poor fit: important requirements are unsupported",
                "partial fit: some relevant evidence but material gaps",
                "strong fit: most central requirements are supported",
                "exceptional fit: direct, substantial evidence for nearly all requirements",
            ],
        ),
        "fit_level": Choice(
            instructions=(
                "Select the candidate's best-supported application positioning for this role "
                "from the supplied profile and job description."
            ),
            criteria={
                "stretch": "Several central requirements lack evidence.",
                "competitive": "The candidate supports many central requirements.",
                "highly_aligned": "The candidate directly supports most central requirements.",
            },
        ),
        "critical_gap": Noul(
            instructions=(
                "Is there a must-have requirement in `job_description` that lacks credible "
                "evidence in `candidate_profile`? Answer yes only for a consequential gap."
            )
        ),
    }

    result = TypeSafeClient().system_one(state=state, questions=questions)
    print(f"Fit score: {result.scores['fit_score'].score}")
    print(f"Fit level: {result.choices['fit_level'].choice}")
    print(f"Critical gap probability: {result.nouls['critical_gap'].noul:.2f}")


if __name__ == "__main__":
    main()
