"""
export.py – Fetch questions from MySQL, serialise them to millionaire.json.

Key improvements over the original:
  - 8 near-identical Static_*/Dynamic_* functions collapsed into two helpers.
  - A single shared DB connection is reused while generating dynamic questions
    instead of opening one per INSERT.
  - Connection / cursor are closed in the correct order (cursor first).
  - generate_json rebuilt for clarity; logic is identical to the original.
"""

from __future__ import annotations

import json
from mysql.connector import Error
import mysql.connector

import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as db_insert

# ---------------------------------------------------------------------------
# Difficulty level → SQL Level column value
# ---------------------------------------------------------------------------
_STATIC_LEVEL: dict[str, int] = {
    "1": 1,   # Primary School
    "2": 2,   # Secondary School
    "3": 3,   # College
    "4": 4,   # Expert
}

# Dynamic selection key → generation tier
_DYNAMIC_TIER: dict[str, str] = {
    "dynamic-1": "easy",
    "dynamic-2": "medium",
    "dynamic-3": "hard",
    "dynamic-4": "expert",
}

_QUESTIONS_PER_GAME = 15


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_connection() -> mysql.connector.MySQLConnection:
    with open("cybermillionaire/util/mysqlPassword.txt") as f:
        password = f.read().strip()
    return mysql.connector.connect(
        host="db",
        database="Millionaire",
        user="root",
        password=password,
    )


def _fetch_static(cursor, level: int) -> list[tuple]:
    """Return 15 randomly ordered questions for a static level (5 per tier)."""
    rows: list[tuple] = []
    for difficulty in ("easy", "medium", "hard"):
        cursor.execute(
            """
            SELECT Question, Ans1, Ans2, Ans3, Ans4, Correct
            FROM millionaire
            WHERE Difficulty = %s AND Level = %s
            ORDER BY RAND()
            LIMIT 5
            """,
            (difficulty, level),
        )
        rows.extend(cursor.fetchall())
    return rows


def _generate_dynamic(cursor, tier: str) -> list[tuple]:
    """
    Generate 15 questions via the Claude API (Claude Fable 5), persist them
    to the `dynamic` table, read them back, then truncate the table.

    Retries on parse failures or model refusals (up to a hard attempt cap)
    so the game still receives a full set of questions.
    """
    max_attempts = _QUESTIONS_PER_GAME * 2  # safety cap on API calls
    inserted = 0
    attempts = 0

    # Reuse one connection for all inserts
    conn = _get_connection()
    try:
        while inserted < _QUESTIONS_PER_GAME and attempts < max_attempts:
            attempts += 1
            try:
                raw = generation.generate_question(tier)
                question, answers, correct = db_insert.parse_question_and_answers(raw)
                db_insert.insert_question_into_db(question, answers, correct, connection=conn)
                inserted += 1
                print(f"Question {inserted}/{_QUESTIONS_PER_GAME} inserted.")
            except generation.GenerationRefusedError as exc:
                print(f"Model declined, retrying – {exc}")
            except Exception as exc:
                print(f"Skipping question, retrying – error: {exc}")
    finally:
        conn.close()

    cursor.execute("SELECT * FROM dynamic LIMIT %s", (_QUESTIONS_PER_GAME,))
    rows = cursor.fetchall()
    cursor.execute("TRUNCATE TABLE dynamic")
    return rows


def _generate_json(rows: list[tuple]) -> None:
    """Serialise *rows* to ``static/js/millionaire.json``."""
    questions = [
        {
            "question": str(row[0]),
            "content":  [str(row[i]) for i in range(1, 5)],
            "correct":  int(row[5]),
        }
        for row in rows
    ]
    payload = {"games": [{"questions": questions}]}
    with open("static/js/millionaire.json", "w") as f:
        json.dump(payload, f)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_questions(selection: str) -> None:
    """
    Fetch (or generate) questions for *selection* and write millionaire.json.

    Valid selections: ``"1"``–``"4"`` (static) or
    ``"dynamic-1"``–``"dynamic-4"`` (dynamic).
    """
    connection = None
    cursor = None
    try:
        connection = _get_connection()
        cursor = connection.cursor()

        if selection in _STATIC_LEVEL:
            rows = _fetch_static(cursor, _STATIC_LEVEL[selection])
        elif selection in _DYNAMIC_TIER:
            rows = _generate_dynamic(cursor, _DYNAMIC_TIER[selection])
        else:
            raise ValueError(f"Invalid selection: {selection!r}")

        _generate_json(rows)

    except Error as exc:
        print(f"MySQL error: {exc}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")
