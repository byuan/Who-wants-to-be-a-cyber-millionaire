import mysql.connector
from mysql.connector import Error
import json
import sys
import cybermillionaire.dynamic_question_generation as generation
import cybermillionaire.database_insert as insert

# Executes all export functionality
def run_sql(cursor, query):
    cursor.execute(query)
    records = cursor.fetchall() #All the records for that query are here.
    return records
    
def generate_json(game):
    json_file = {}
    json_file['games'] = []
    questions = []

    for question in game:
        #for column in question:
        for i in range(len(question)):
            # Need to include "questions" around the individual question
            if i == 0:
                quest_json = question[i]
            # Surround answers with [],
            if i == 1:
                ans1_json = question[i]
            if i == 2:
                ans2_json = question[i]
            if i == 3:
                ans3_json = question[i]
            if i == 4:
                ans4_json = question[i]
            if i == 5:
                correct_json = question[i]
                                 
        #create content array
        content = []
        content.append(str(ans1_json))
        content.append(str(ans2_json))
        content.append(str(ans3_json))
        content.append(str(ans4_json))

        # populate questions dictionary
        questions.append({
            "question": str(quest_json),
            "content" : content,
            "correct": int(correct_json)
        })
    json_file['games'].append({"questions" : questions})

    with open('static/js/millionaire.json','w') as outfile:
        json.dump(json_file, outfile)

# This will run when a Static Primary School game is selected. It will gather all questions for the game       
def Static_Primary_School(cursor):
    game = []

    # Gets the 5 easy questions for the Static Primary School game
    sql_Primary_T1 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'easy' AND Level = 1 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Primary_T1)
    #save everything as variables
    for row in result:
        game.append(row)

        
    # Gets the 5 medium questions for the Static Primary School game
    sql_Primary_T2 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'medium' and Level = 1 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Primary_T2)
    #save everything as variables
    for row in result:
        game.append(row)

    # Gets the 5 hard questions for the Static Primary School game
    sql_Primary_T3 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'hard' and Level = 1 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Primary_T3)
    #save everything as variables
    for row in result:
        game.append(row)

    return game


# This will run when a Static Secondary School game is selected. It will gather all questions for the game
def Static_Secondary_School(cursor):
    game = []

    # Gets the 5 easy questions for the Static Secondary School game
    sql_Secondary_T1 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'easy' AND Level = 2 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Secondary_T1)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Gets the 5 medium questions for the Static Secondary School game
    sql_Secondary_T2 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'medium' AND Level = 2 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Secondary_T2)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Gets the 5 hard questions for the Static Secondary School game
    sql_Secondary_T3 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'hard' AND Level = 2 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Secondary_T3)
    #save everything as variables 
    for row in result:
        game.append(row)

    return game


# This will run when a Static College game is selected. It will gather all questions for the game.
def Static_College(cursor):
    game = []

    # Gets the 5 easy questions for the Static College game
    sql_College_T1 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'easy' AND Level = 3 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_College_T1)
    #save everything as variables 
    for row in result:
        game.append(row)


    # Gets the 5 medium questions for the Static College game
    sql_College_T2 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'medium' AND Level = 3 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_College_T2)
    #save everything as variables
    for row in result:
        game.append(row)

    # Gets the 5 hard questions for the Static College game
    sql_College_T3 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'hard' AND Level = 3 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_College_T3)
    #save everything as variables
    for row in result:
        game.append(row)

    return game


# This will run when a Static Expert game is selected. It will gather all questions for the game
def Static_Expert(cursor):
    game = []

    # Gets the 5 easy questions for the Static Expert game
    sql_Expert_T1 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'easy' AND Level = 4 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Expert_T1)
    #save everything as variables
    for row in result:
        game.append(row)


    # Gets the 5 medium questions for the Static Expert game
    sql_Expert_T2 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'medium' AND Level = 4 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Expert_T2)
    #save everything as variables
    for row in result:
        game.append(row)

    # Gets the 5 hard questions for the Static Expert game
    sql_Expert_T3 = "select Question, Ans1, Ans2, Ans3, Ans4, Correct, Difficulty, Level FROM millionaire WHERE Difficulty = 'hard' AND Level = 4 ORDER BY rand() LIMIT 5;"
    result = run_sql(cursor, sql_Expert_T3)
    #save everything as variables
    for row in result:
        game.append(row)
    
    return game


# DYNAMIC
# This will run when a dynamic primary school game is selected. It will gather all questions for the game and then empty the dynamic table.
def Dynamic_Primary_School(cursor):
    game = []
    
    for i in range(0, 20):
        question_text = generation.generate_question("easy")

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            insert.insert_question_into_db(question, answers, correct_answer)
            print("Question inserted successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    # add questions from database to game
    sql_dynamic_primary = "SELECT * FROM dynamic LIMIT 15;"
    result = run_sql(cursor, sql_dynamic_primary)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Clear the dynamic table
    cursor.execute("TRUNCATE TABLE dynamic;")

    return game

# This will run when a dynamic secondary school game is selected. It will gather all questions for the game.
def Dynamic_Secondary_School(cursor):
    game = []
    
    for i in range(0, 20):
        question_text = generation.generate_question("medium")

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            insert.insert_question_into_db(question, answers, correct_answer)
            print("Question inserted successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    # add questions from database to game
    sql_dynamic_secondary = "SELECT * FROM dynamic LIMIT 15;"
    result = run_sql(cursor, sql_dynamic_secondary)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Clear the dynamic table
    cursor.execute("TRUNCATE TABLE dynamic;")

    return game

# This will run when a dynamic college game is selected. It will gather all questions for the game.
def Dynamic_College(cursor):
    game = []
    
    for i in range(0, 20):
        question_text = generation.generate_question("hard")

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            insert.insert_question_into_db(question, answers, correct_answer)
            print("Question inserted successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    # add questions from database to game
    sql_dynamic_college = "SELECT * FROM dynamic LIMIT 15;"
    result = run_sql(cursor, sql_dynamic_college)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Clear the dynamic table
    cursor.execute("TRUNCATE TABLE dynamic;")

    return game

# This will run when a dynamic expert game is selected. It will gather all questions for the game.
def Dynamic_Expert(cursor):
    game = []
    
    for i in range(0, 20):
        question_text = generation.generate_question("expert")

        try:
            question, answers, correct_answer = insert.parse_question_and_answers(question_text)
            insert.insert_question_into_db(question, answers, correct_answer)
            print("Question inserted successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

    # add questions from database to game
    sql_dynamic_expert = "SELECT * FROM dynamic LIMIT 15;"
    result = run_sql(cursor, sql_dynamic_expert)
    #save everything as variables 
    for row in result:
        game.append(row)

    # Clear the dynamic table
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
    
    if selection == '1':
        game = Static_Primary_School(cursor)

    elif selection == '2':
        game = Static_Secondary_School(cursor)

    elif selection == '3':
        game = Static_College(cursor)

    elif selection == '4':
        game = Static_Expert(cursor)

    elif selection == 'dynamic-1':
        game = Dynamic_Primary_School(cursor)

    elif selection == 'dynamic-2':
        game = Dynamic_Secondary_School(cursor)

    elif selection == 'dynamic-3':
        game = Dynamic_College(cursor)

    elif selection == 'dynamic-4':
        game = Dynamic_Expert(cursor)

    else:
        print("Invalid Level Selection!")
    
    generate_json(game)

    if (connection.is_connected()):
        connection.close()
        cursor.close()
        print("MySQL connection is closed")