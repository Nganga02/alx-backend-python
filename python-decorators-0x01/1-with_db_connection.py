import sqlite3 
from functools import wraps 


def with_db_connection(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        user = func(conn, *args, **kwargs)
        conn.close()
        return user
    return wrapper_func


@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 
    #### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=2)
print(user)