from __future__ import annotations

import re
import mysql.connector
from mysql.connector import Error


def _get_db_password() -> str:
    """Read the MySQL password once from disk."""
    with open("cybermillionaire/util/mysqlPassword.txt") as f:
        return f.read().strip()


def get_connection() -> mysql.connector.MySQLConnection:
    """Return a new MySQL connection using the stored credentials."""
    return mysql.connector.connect(
        host="db",
        database="Millionaire",
        user="root",
        password=_get_db_password(),
    )


def parse_question_and_answers(text: str) -> tuple[str, list[str], int]:
    """
    Parse the GPT response text into (question, [ans1..ans4], correct_index).

    Raises ValueError if the expected fields are missing.
    """
    # Strip markdown emphasis (e.g. "**Question:**") that capable models
    # sometimes add despite format instructions.
    text = text.replace("**", "").replace("__", "")

    question_match = re.search(r"Question:\s*(.+)", text)
    answers_match = re.findall(r"[A-D]\.\s*([^\n]+)", text)
    correct_match = re.search(r"Correct Answer:\s*([A-D])", text)

    if not question_match or len(answers_match) < 4 or not correct_match:
        raise ValueError(f"Unable to parse GPT response:\n{text}")

    question = question_match.group(1).strip()
    answers = [a.strip() for a in answers_match[:4]]
    correct_index = ord(correct_match.group(1)) - ord("A")

    return question, answers, correct_index


def insert_question_into_db(
    question: str,
    answers: list[str],
    correct_answer: int,
    connection: mysql.connector.MySQLConnection | None = None,
) -> None:
    """
    Insert a parsed question into the `dynamic` table.

    Accepts an optional existing *connection* so callers that insert many
    rows in a loop can reuse a single connection instead of opening a new
    one per row.
    """
    own_connection = connection is None
    try:
        if own_connection:
            connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO dynamic (Question, Ans1, Ans2, Ans3, Ans4, Correct)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (question, *answers, correct_answer),
            )
        connection.commit()

    except Error as exc:
        raise RuntimeError(f"MySQL insert failed: {exc}") from exc
    finally:
        if own_connection and connection is not None:
            connection.close()
