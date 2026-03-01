#!/usr/bin/env python3
"""Lightweight AI-style reviewer for QMS documents.

This script performs a heuristic review of QMS text documents and reports
coverage across common compliance sections.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float
    found_keywords: List[str]
    message: str


CHECKS: Dict[str, Sequence[str]] = {
    "Document control metadata": (
        "title",
        "version",
        "effective date",
        "owner",
        "approved by",
        "reviewed by",
    ),
    "Purpose and scope": (
        "purpose",
        "scope",
        "objective",
        "applies to",
    ),
    "Roles and responsibilities": (
        "responsibility",
        "responsible",
        "role",
        "authority",
        "accountable",
    ),
    "Process flow and steps": (
        "procedure",
        "step",
        "workflow",
        "sequence",
        "process",
    ),
    "Risk management": (
        "risk",
        "hazard",
        "mitigation",
        "severity",
        "probability",
    ),
    "CAPA and nonconformance": (
        "capa",
        "nonconformance",
        "corrective action",
        "preventive action",
        "root cause",
    ),
    "Records and retention": (
        "record",
        "retention",
        "archive",
        "traceability",
        "documented information",
    ),
}


def normalize_text(text: str) -> str:
    """Normalize whitespace and lowercase for matching."""
    return re.sub(r"\s+", " ", text).lower().strip()


def evaluate_check(name: str, keywords: Sequence[str], text: str) -> CheckResult:
    """Evaluate a single checklist against the document text."""
    hits = [kw for kw in keywords if kw in text]
    score = len(hits) / max(len(keywords), 1)
    passed = score >= 0.4

    if passed:
        message = f"{name}: appears covered ({len(hits)}/{len(keywords)} indicators found)."
    else:
        message = (
            f"{name}: potential gap ({len(hits)}/{len(keywords)} indicators found). "
            "Consider adding explicit language."
        )

    return CheckResult(
        name=name,
        passed=passed,
        score=round(score, 2),
        found_keywords=hits,
        message=message,
    )


def review_document(path: Path) -> Dict[str, object]:
    """Review a document and return structured findings."""
    raw = path.read_text(encoding="utf-8")
    text = normalize_text(raw)

    check_results = [evaluate_check(name, keywords, text) for name, keywords in CHECKS.items()]

    overall_score = round(sum(result.score for result in check_results) / len(check_results), 2)
    status = "Pass" if overall_score >= 0.6 else "Needs Improvement"

    return {
        "document": str(path),
        "overall_score": overall_score,
        "status": status,
        "results": [
            {
                "check": result.name,
                "passed": result.passed,
                "score": result.score,
                "found_keywords": result.found_keywords,
                "message": result.message,
            }
            for result in check_results
        ],
    }


def print_human_report(report: Dict[str, object]) -> None:
    """Print a human-readable report."""
    print(f"QMS AI Review: {report['document']}")
    print(f"Overall Score: {report['overall_score']} | Status: {report['status']}")
    print("-" * 72)

    for item in report["results"]:
        icon = "✔" if item["passed"] else "✖"
        print(f"{icon} {item['check']} (score={item['score']})")
        print(f"   {item['message']}")
        if item["found_keywords"]:
            print(f"   Found: {', '.join(item['found_keywords'])}")
        else:
            print("   Found: none")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-style QMS document reviewer")
    parser.add_argument("document", type=Path, help="Path to .txt or .md document")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.document.exists():
        raise FileNotFoundError(f"Document not found: {args.document}")

    report = review_document(args.document)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_report(report)


if __name__ == "__main__":
    main()
