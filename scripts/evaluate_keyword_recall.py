import json
import sys
from pathlib import Path


def score_case(case: dict) -> dict:
    resume = case["resume"].lower()
    expected = case.get("expected_keywords", [])
    matched = [keyword for keyword in expected if keyword.lower() in resume]
    recall = round((len(matched) / max(len(expected), 1)) * 100)
    return {
        "id": case["id"],
        "recall": recall,
        "matched": matched,
        "missing": [keyword for keyword in expected if keyword not in matched],
    }


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/eval_cases.jsonl")
    results = [
        score_case(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    average = round(sum(item["recall"] for item in results) / max(len(results), 1))
    print(json.dumps({"average_keyword_recall": average, "cases": results}, indent=2))


if __name__ == "__main__":
    main()
