"""
Load GROQ_API_KEY for lessons that call Groq (6–7).

Students supply their own key — create one at https://console.groq.com and save it
in a .env file (lesson folder or /home/voicedevice/.env):

  GROQ_API_KEY=gsk_...
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_a, **_k):
        return False


ENV_CANDIDATES = (
    Path("/home/voicedevice/.env"),
    Path("/opt/voicedevice/.env"),
)


def load_groq_config(lesson_dir: Path | None = None) -> tuple[str, Path | None]:
    """Load GROQ_API_KEY from .env files. Returns (api_key, last_path_loaded)."""
    paths: list[Path] = []
    for p in ENV_CANDIDATES:
        if p.is_file():
            paths.append(p)
    if lesson_dir is not None:
        local = lesson_dir / ".env"
        if local.is_file():
            paths.append(local)

    last_path: Path | None = None
    for p in paths:
        load_dotenv(p, override=True)
        last_path = p

    if not paths:
        load_dotenv()

    key = os.getenv("GROQ_API_KEY", "").strip()
    return key, last_path


def missing_groq_key_message() -> str:
    return (
        "GROQ_API_KEY is not set.\n\n"
        "1) Create a free API key at https://console.groq.com\n"
        "2) Save it in a .env file next to your lesson, or in ~/lessons/.env:\n\n"
        "     GROQ_API_KEY=gsk_your_key_here\n\n"
        "3) Run the lesson again."
    )


def require_groq_key(lesson_dir: Path | None = None) -> str:
    key, _ = load_groq_config(lesson_dir)
    if not key:
        raise RuntimeError(missing_groq_key_message())
    return key
