"""Database migrations for the Video Analytics application."""

from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent
SQL_FILES = sorted(MIGRATIONS_DIR.glob("*.sql"))

__all__ = ["MIGRATIONS_DIR", "SQL_FILES"] 