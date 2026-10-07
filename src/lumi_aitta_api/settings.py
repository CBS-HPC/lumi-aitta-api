from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


def load_env(path: Path = Path(".env")) -> None:
    """Load literal values without shell evaluation or printing credentials."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        key, separator, value = line.strip().partition("=")
        if separator and re.fullmatch(r"[A-Z][A-Z0-9_]*", key.strip()):
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)

    def __post_init__(self):
        if not isinstance(self.api_key, str) or not self.api_key or any(
                ord(char) < 32 or ord(char) > 126 for char in self.api_key):
            raise ValueError("AITTA_API_KEY must be a nonempty printable token")

    @classmethod
    def from_env(cls) -> Settings:
        return cls(api_key=os.getenv("AITTA_API_KEY", ""))
