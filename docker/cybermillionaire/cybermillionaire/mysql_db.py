import mysql.connector
from mysql.connector import Error


def get_connection():

    try:
        connection = mysql.connector.connect(
            host="db",
            database="Millionaire",
            user="root",
            password=open(
                "cybermillionaire/util/mysqlPassword.txt"
            ).read().strip()
        )

        return connection

    except Error as e:
        print("MySQL connection error:", e)
        return None
    
def save_topic_settings(user_id, settings):
    connection = get_connection()
    cursor = connection.cursor()
    # remove old settings
    cursor.execute(
        """
        DELETE FROM topic_settings
        WHERE user_id = %s
        """,
        (user_id,)
    )

    for difficulty, topics in settings.items():
        for topic in topics:
            cursor.execute(
                """
                INSERT INTO topic_settings
                (
                    user_id,
                    difficulty,
                    topic
                )
                VALUES (%s,%s,%s)
                """,
                (
                    user_id,
                    difficulty,
                    topic
                )
            )

    connection.commit()

    cursor.close()
    connection.close()

def get_topic_settings(user_id):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT difficulty, topic
        FROM topic_settings
        WHERE user_id = %s
        """,
        (user_id,)
    )


    rows = cursor.fetchall()
    settings = {
        "easy": [],
        "medium": [],
        "hard": [],
        "expert": []
    }

    for row in rows:
        settings[row["difficulty"]].append(
            row["topic"]
        )

    cursor.close()
    connection.close()
    return settings

def get_or_create_user(username):

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute(
            """
            INSERT INTO users(username)
            VALUES(%s)
            """,
            (username,)
        )
        connection.commit()
        user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return user_id