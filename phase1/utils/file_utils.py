import json
from typing import Any

def is_valid_json(filepath: str) -> bool:
    try:
        with open(filepath, "r") as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False
    
import json

def load_json(filename: str) -> Any:
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    return None
