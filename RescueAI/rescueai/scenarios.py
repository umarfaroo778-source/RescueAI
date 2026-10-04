import json
from pathlib import Path

def load_scenarios():
    return json.loads((Path(__file__).parent.parent / "data" / "scenarios.json").read_text(encoding="utf-8"))
