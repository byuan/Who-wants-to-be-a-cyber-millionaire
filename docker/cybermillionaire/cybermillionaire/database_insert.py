import mysql.connector
import re
from mysql.connector import Error

# Function to parse the returned text and remove the A, B, C, D labels
def parse_question_and_answers(text):
    if not isinstance(text, str):
        raise ValueError("Question response must be text")
    question_match = re.search(r"^Question:\s*([^\n]+)$", text, re.IGNORECASE | re.MULTILINE)
    choices = re.findall(r"^([A-D])\.\s*([^\n]+)$", text, re.IGNORECASE | re.MULTILINE)
    correct_matches = re.findall(r"^Correct Answer:\s*([A-D])\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not question_match or len(choices) != 4 or len(correct_matches) != 1:
        raise ValueError("Expected a question, four choices, and one correct answer")
    labels = [label.upper() for label, _ in choices]
    answers = [answer.strip() for _, answer in choices]
    if labels != list("ABCD") or any(not answer for answer in answers):
        raise ValueError("Choices must be labeled A through D in order")
    if len({answer.casefold() for answer in answers}) != 4:
        raise ValueError("Answers must be unique")
    return question_match.group(1).strip(), answers, ord(correct_matches[0].upper()) - ord("A")

# Function to insert the parsed data into the database
def insert_question_into_db(question, answers, correct_answer):
    # Connect to MySQL
    try:
    
        f = open("cybermillionaire/util/mysqlPassword.txt")
        conn = mysql.connector.connect(host='db',
                                         database='Millionaire',
                                         user='root',
                                         password= f.read().strip())
        cursor = conn.cursor()
    
    except Error as e:
        print("Error reading data from MySQL table", e)
    

    # Insert query
    insert_query = '''
    INSERT INTO dynamic (Question, Ans1, Ans2, Ans3, Ans4, Correct)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''

    # Data to insert
    data = (
        question,
        answers[0],  # Ans1
        answers[1],  # Ans2
        answers[2],  # Ans3
        answers[3],  # Ans4
        correct_answer  # Correct answer is an integer (1-4)
    )

    # Execute the query
    cursor.execute(insert_query, data)

    # Commit the transaction
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()
