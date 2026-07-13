import mysql.connector
from mysql.connector import Error
import json
import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert

# Executes all export functionality
def run_sql(cursor, query, param=None):
    if param:
        cursor.execute(query, param)
    else:
        cursor.execute(query)
    records = cursor.fetchall() #All the records for that query are here.
    return records
    
def generate_json(game):
    json_file = {}
    json_file["games"] = []

    questions = []

    for question in game:

        quest_json = question[0]
        ans1_json = question[1]
        ans2_json = question[2]
        ans3_json = question[3]
        ans4_json = question[4]
        correct_json = question[5]

        questions.append({
            "question": str(quest_json),
            "content": [
                str(ans1_json),
                str(ans2_json),
                str(ans3_json),
                str(ans4_json)
            ],
            "correct": int(correct_json)
        })

    json_file["games"].append({
        "questions": questions
    })

    return json_file

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
def Dynamic_Game(cursor, difficulty_level):
    game = []

    # map your difficulty strings to AI input
    level_map = {
        "primary": "easy",
        "secondary": "medium",
        "college": "hard",
        "expert": "expert"
    }

    ai_level = level_map[difficulty_level]

    # 1. Generate questions + insert into DB
    count = 0
    while count < 15:
        question_text = generation.generate_question(ai_level)

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            insert.insert_question_into_db(question, answers, correct_answer)
            count += 1
        except Exception as e:
            print(f"Generation error: {e}")
            continue

    result = run_sql(cursor, "SELECT * FROM dynamic LIMIT 15;")

    for row in result:
        game.append(row)

    cursor.execute("TRUNCATE TABLE dynamic;")

    return game

#def main():
def export_questions(selection):
    # export questions from mysql based on a given level
    game = []
    try:
    
        f = open("cybermillionaire/util/mysqlPassword.txt")
        connection = mysql.connector.connect(host='db',
                                         database='Millionaire',
                                         user='root',
                                         password= f.read().strip())
        cursor = connection.cursor()
    
    except Error as e:
        print("Error reading data from MySQL table", e)
    
    if selection == '1' or selection == '2' or selection == '3' or selection == '4':
        game = Static_Game(cursor,selection)

    elif selection == 'dynamic-1':
        game = Dynamic_Game(cursor,"primary")

    elif selection == 'dynamic-2':
        game = Dynamic_Game(cursor,"secondary")

    elif selection == 'dynamic-3':
        game = Dynamic_Game(cursor,"college")

    elif selection == 'dynamic-4':
        game = Dynamic_Game(cursor,"expert")

    else:
        print("Invalid Level Selection!")
    
    json_game = generate_json(game)

    if (connection.is_connected()):
        connection.close()
        cursor.close()
        print("MySQL connection is closed")

    return json_game