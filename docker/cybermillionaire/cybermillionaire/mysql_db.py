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