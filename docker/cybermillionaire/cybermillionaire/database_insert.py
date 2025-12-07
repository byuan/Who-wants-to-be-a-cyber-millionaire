from pathlib import Path
import mysql.connector
from mysql.connector import Error
import re

PASSWORD_FILE = Path("cybermillionaire/util/mysqlPassword.txt")


def _read_password():
    return PASSWORD_FILE.read_text().strip()

# Function to parse the returned text and remove the A, B, C, D labels
def parse_question_and_answers(text):
    # Regular expression to extract the question and answers
    question_match = re.search(r"Question: (.*?)\n", text)
    answers_match = re.findall(r"([A-D])\.\s([^\n]+)", text)  # Matches A. Answer text, B. Answer text, etc.
    correct_answer_match = re.search(r"Correct Answer: ([A-D])", text)  # Matches Correct Answer: A, B, C, or D

    if not question_match or not answers_match or not correct_answer_match:
        raise ValueError("Unable to parse the text correctly")

    question = question_match.group(1)
    answers = [a[1].strip() for a in answers_match]  # Extract answer texts and strip extra spaces
    correct_letter = correct_answer_match.group(1)  # The correct letter (e.g., A, B, C, D)
    
    # Convert the correct letter (A-D) to a 0-based index
    correct_answer = ord(correct_letter) - ord('A')

    return question, answers, correct_answer

def create_connection():
    password = _read_password()
    return mysql.connector.connect(
        host="db", database="Millionaire", user="root", password=password
    )


# Function to insert the parsed data into the database
def insert_question_into_db(question, answers, correct_answer, connection=None):
    managed_connection = connection or create_connection()
    cursor = managed_connection.cursor()

    try:
        insert_query = (
            "INSERT INTO dynamic (Question, Ans1, Ans2, Ans3, Ans4, Correct) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        data = (
            question,
            answers[0],  # Ans1
            answers[1],  # Ans2
            answers[2],  # Ans3
            answers[3],  # Ans4
            correct_answer,  # Correct answer is a 0-based index
        )

        cursor.execute(insert_query, data)
        managed_connection.commit()
    except Error as exc:
        print("Error inserting data into MySQL table", exc)
    finally:
        cursor.close()
        if connection is None:
            managed_connection.close()
