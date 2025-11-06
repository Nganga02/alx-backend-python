import sqlite3
from functools import wraps

#### decorator to log SQL queries
from datetime import datetime
def log_queries(func):
    @wraps(func)
    def wrapper_log(*args, **kwargs):

        query = kwargs.get('query') or (args[0] if args else None)
        print(f"{datetime.now()} : {list(kwargs.keys())[0].upper()} : {query}")  
        result = func(*args, **kwargs)
        return result
    return wrapper_log

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="""SELECT * FROM users""")
print(users)