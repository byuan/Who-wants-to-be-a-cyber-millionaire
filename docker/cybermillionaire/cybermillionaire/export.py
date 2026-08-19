import mysql.connector
from mysql.connector import Error
import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert
import traceback

# Executes all export functionality
def run_sql(cursor, query, param=None):
    if param:
        cursor.execute(query, param)
    else:
        cursor.execute(query)
    records = cursor.fetchall() #All the records for that query are here.
    return records
    
def format_game_data(game):

    questions = []
    for question in game:
        # Dynamic AI generated question
        if isinstance(question, dict):
            questions.append({
                "question": question["question"],
                "content": question["answers"],
                "correct": int(question["correct_answer"])
            })

        # Static SQL question
        else:
            questions.append({
                "question": question[0],
                "content": [question[1],question[2],question[3],question[4]],
                "correct": int(question[5])
            })

    return {
        "games": [{"questions": questions}]
    }

# This will run when a Static Primary School game is selected. It will gather all questions for the game       
def Static_Game(cursor, level):
    game = []

    difficulties = ["easy", "medium", "hard"]

    for diff in difficulties:
        sql = """
        SELECT Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level
        FROM millionaire
        WHERE Difficulty = %s AND Level = %s
        ORDER BY rand()
        LIMIT 5;
        """

        result = run_sql(cursor, sql, (diff, level))

        for row in result:
            game.append(row)

    return game

# DYNAMIC
# This will run when a dynamic primary school game is selected. It will gather all questions for the game and then empty the dynamic table.
def Dynamic_Game(difficulty_level, user_id, count=15):

    game = []

    level_map = {
        "primary": "easy",
        "secondary": "medium",
        "college": "hard",
        "expert": "expert"
    }

    ai_level = level_map[difficulty_level]
    while len(game) < count:
        question_text = generation.generate_question(
            ai_level,
            user_id
        )
        try:

            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            game.append({"question": question,"answers": answers,"correct_answer": correct_answer})

        except Exception as e:
            print(f"Generation error:, {e}")
            traceback.print_exc()

    return game

def export_questions(selection, user_id=None):
    game = []
    if selection == '1' or selection == '2' or selection == '3' or selection == '4':
        try:
            f = open("cybermillionaire/util/mysqlPassword.txt")

            connection = mysql.connector.connect(
                host='db',
                database='Millionaire',
                user='root',
                password=f.read().strip()
            )
            cursor = connection.cursor()

        except Error as e:
            print("Error reading data from MySQL table", e)

        game = Static_Game(cursor, selection)

        if connection.is_connected():
            cursor.close()
            connection.close()


    elif selection == 'dynamic-1':
        game = Dynamic_Game("primary", user_id)

    elif selection == 'dynamic-2':
        game = Dynamic_Game("secondary", user_id)

    elif selection == 'dynamic-3':
        game = Dynamic_Game("college", user_id)

    elif selection == 'dynamic-4':
        game = Dynamic_Game("expert", user_id)

    else:
        print("Invalid Level Selection!")

    return format_game_data(game)