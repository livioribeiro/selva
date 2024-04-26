from datetime import date, time, timedelta
from types import NoneType


def _ensure_json(data, recursion_limit: int = 4, recursion_depth: int = 0):
    recursion_depth += 1
    if recursion_depth > recursion_limit:
        return str(data)

    if isinstance(data, dict):
        return {
            k: _ensure_json(v, recursion_limit, recursion_depth)
            for k, v in data.items()
            if v is not None
        }
    if isinstance(data, list):
        return [
            _ensure_json(v, recursion_limit, recursion_depth)
            for v in data
            if v is not None
        ]

    if isinstance(data, (date, time)):
        return data.isoformat()

    if isinstance(data, (str, int, float, bool, NoneType)):
        return data

    return str(data)
