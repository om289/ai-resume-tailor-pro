import argparse
import json
from pathlib import Path


SYSTEM = "You tailor resumes without inventing experience."


def main() -> None:
    parser = argparse.ArgumentParser(description="Append one fine-tuning example to JSONL.")
    parser.add_argument("--resume", required=True, help="Path to resume text.")
    parser.add_argument("--job", required=True, help="Path to job description text.")
    parser.add_argument("--output", required=True, help="Path to ideal assistant output text.")
    parser.add_argument("--dataset", default="data/train_examples.jsonl")
    args = parser.parse_args()

    resume = Path(args.resume).read_text(encoding="utf-8").strip()
    job = Path(args.job).read_text(encoding="utf-8").strip()
    ideal = Path(args.output).read_text(encoding="utf-8").strip()
    item = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Resume: {resume}\n\nJob: {job}"},
            {"role": "assistant", "content": ideal},
        ]
    }
    with Path(args.dataset).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
