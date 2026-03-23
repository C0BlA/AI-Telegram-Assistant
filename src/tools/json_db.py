import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def load_json(file_name: str):
    path = BASE_DIR / "src" / "data" / file_name

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_name: str, data):
    path = BASE_DIR / "src" / "data" / file_name

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)