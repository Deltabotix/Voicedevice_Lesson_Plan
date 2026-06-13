"""Lesson 2 entry — runs challenge.py (edit challenge.py for the lesson)."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "challenge.py"), run_name="__main__")
