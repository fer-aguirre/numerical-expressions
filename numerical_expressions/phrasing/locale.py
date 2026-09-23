from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from num2words import num2words

LOCALES_DIR = Path(__file__).parent / "locales"


def available_locales() -> List[str]:
    return sorted(path.stem for path in LOCALES_DIR.glob("*.json"))


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_data(code: str) -> Dict[str, Any]:
    path = LOCALES_DIR / f"{code}.json"
    if not path.is_file():
        raise ValueError(f"Unknown language: {code} (available: {', '.join(available_locales())})")
    data = json.loads(path.read_text(encoding="utf-8"))
    parent = data.pop("extends", None)
    return _deep_merge(_load_data(parent), data) if parent else data


class Locale:
    """The templates and number conventions for one language, loaded from locales/<code>.json."""

    def __init__(self, code: str, data: Dict[str, Any]):
        self.code = code
        self.language = code.split("-")[0]
        self.data = data
        self._contractions = [
            (re.compile(rf"\b{re.escape(source)}\b"), target)
            for source, target in data.get("contractions", {}).items()
        ]

    def get(self, key: str, default: Any = None) -> Any:
        value: Any = self.data
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def t(self, key: str, **kwargs: Any) -> str:
        template = self.get(key)
        if template is None:
            raise KeyError(f"Missing template '{key}' for language '{self.code}'")
        return template.format(**kwargs)

    def words(self, number: int) -> str:
        return num2words(number, lang=self.data["num2words"])

    def finish(self, text: str) -> str:
        """Apply the language's contractions, e.g. Spanish "de el" -> "del"."""
        for pattern, target in self._contractions:
            text = pattern.sub(target, text)
        return text


@lru_cache(maxsize=None)
def load_locale(code: str) -> Locale:
    return Locale(code, _load_data(code))
