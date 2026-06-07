import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import DB_PATH, init_db


def main() -> None:
    init_db()
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
