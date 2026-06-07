import csv
import sqlite3
import sys
from pathlib import Path


DB_PATH = Path("storage/app.db")


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("storage/feedback_export.csv")
    if not DB_PATH.exists():
        raise SystemExit("No database found. Run the app and save feedback first.")

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT
              feedback.id,
              feedback.run_id,
              feedback.rating,
              feedback.comment,
              feedback.created_at,
              runs.role,
              runs.source,
              runs.model_name,
              runs.score
            FROM feedback
            JOIN runs ON runs.id = feedback.run_id
            ORDER BY feedback.created_at DESC
            """
        ).fetchall()

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["feedback_id", "run_id", "rating", "comment", "created_at", "role", "source", "model_name", "score"]
        )
        writer.writerows(rows)

    print(f"Exported {len(rows)} feedback rows to {output}")


if __name__ == "__main__":
    main()
