from django.db import connection

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query,params or [])
        return cursor.fetchall()

def execute_insert(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query,params or [])
        return cursor.lastrowid