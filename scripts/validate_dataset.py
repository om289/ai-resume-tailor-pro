import json
import sys
from pathlib import Path


def validate(path: Path) -> dict:
    issues = []
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append(f"Line {line_number}: invalid JSON: {exc}")
            continue
        messages = item.get("messages")
        if not isinstance(messages, list) or len(messages) < 3:
            issues.append(f"Line {line_number}: expected at least 3 messages")
            continue
        roles = [message.get("role") for message in messages]
        if roles[:3] != ["system", "user", "assistant"]:
            issues.append(f"Line {line_number}: first roles must be system/user/assistant")
        for index, message in enumerate(messages, 1):
            if not isinstance(message.get("content"), str) or not message["content"].strip():
                issues.append(f"Line {line_number}, message {index}: missing content")
    return {"valid": not issues, "count": count, "issues": issues}


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/train_examples.jsonl")
    result = validate(path)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
