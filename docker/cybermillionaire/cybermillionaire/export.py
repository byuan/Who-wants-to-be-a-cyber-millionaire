import json
from mysql.connector import Error

import cybermillionaire.database_insert as insert
import cybermillionaire.dynamic_question_generation as generation

QUESTION_DIFFICULTIES = ("easy", "medium", "hard")
STATIC_LEVELS = {"1": 1, "2": 2, "3": 3, "4": 4}
DYNAMIC_LEVELS = {
    "dynamic-1": "easy",
    "dynamic-2": "medium",
    "dynamic-3": "hard",
    "dynamic-4": "expert",
}
TOTAL_DYNAMIC_QUESTIONS = 15


def generate_json(game):
    questions = []

    for question in game:
        quest_json, ans1_json, ans2_json, ans3_json, ans4_json, correct_json, *_ = question
        content = [
            str(ans1_json),
            str(ans2_json),
            str(ans3_json),
            str(ans4_json),
        ]
        questions.append(
            {
                "question": str(quest_json),
                "content": content,
                "correct": int(correct_json),
            }
        )

    with open("static/js/millionaire.json", "w") as outfile:
        json.dump({"games": [{"questions": questions}]}, outfile)


def fetch_questions_for_level(cursor, level):
    game = []
    query = (
        "SELECT Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level "
        "FROM millionaire WHERE Difficulty = %s AND Level = %s "
        "ORDER BY rand() LIMIT 5;"
    )

    for difficulty in QUESTION_DIFFICULTIES:
        cursor.execute(query, (difficulty, level))
        game.extend(cursor.fetchall())

    return game


def generate_dynamic_questions(connection, difficulty, total_questions=TOTAL_DYNAMIC_QUESTIONS):
    for _ in range(total_questions):
        question_text = generation.generate_question(difficulty)

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(
                question_text
            )
            insert.insert_question_into_db(
                question, answers, correct_answer, connection=connection
            )
            print("Question inserted successfully!")
        except Exception as exc:  # noqa: BLE001
            print(f"An error occurred: {exc}")


def dynamic_game(cursor, connection, difficulty):
    generate_dynamic_questions(connection, difficulty)
    cursor.execute(
        "SELECT Question, Ans1, Ans2, Ans3, Ans4, Correct FROM dynamic LIMIT %s;",
        (TOTAL_DYNAMIC_QUESTIONS,),
    )
    game = cursor.fetchall()
    cursor.execute("TRUNCATE TABLE dynamic;")
    connection.commit()
    return game


def export_questions(selection):
    if selection not in {*STATIC_LEVELS.keys(), *DYNAMIC_LEVELS.keys()}:
        print("Invalid Level Selection!")
        return

    try:
        connection = insert.create_connection()
        cursor = connection.cursor()
    except Error as e:
        print("Error reading data from MySQL table", e)
        return

    try:
        if selection in STATIC_LEVELS:
            game = fetch_questions_for_level(cursor, STATIC_LEVELS[selection])
        else:
            game = dynamic_game(cursor, connection, DYNAMIC_LEVELS[selection])

        generate_json(game)
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
