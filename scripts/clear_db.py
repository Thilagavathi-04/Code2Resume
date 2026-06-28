#!/usr/bin/env python3
"""Clear all user data from PostgreSQL and ChromaDB."""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"

TABLES_IN_ORDER = [
    "activity_logs",
    "skill_gap_analyses",
    "interview_sessions",
    "ats_reports",
    "job_descriptions",
    "generated_resumes",
    "certifications",
    "skills",
    "experiences",
    "educations",
    "projects",
    "resumes",
    "users",
]


def clear_postgres(url: str):
    engine = create_engine(url.replace("+asyncpg", ""))
    with engine.begin() as conn:
        for table in TABLES_IN_ORDER:
            conn.execute(text(f'TRUNCATE TABLE {table} CASCADE'))
            print(f"  Truncated {table}")
    engine.dispose()


def clear_chromadb():
    if not CHROMA_DIR.exists():
        print("  chroma_db/ does not exist, skipping")
        return
    for child in CHROMA_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    print(f"  Cleared {CHROMA_DIR}")


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return

    print("Clearing PostgreSQL...")
    clear_postgres(db_url)

    print("Clearing ChromaDB...")
    clear_chromadb()

    print("Done. All user data cleared.")


if __name__ == "__main__":
    main()
