import sqlite3 
import functools
import time

db_connection = __import__('1-with_db_connection')
with_db_connection = db_connection.with_db_connection

def transactional(func):
    """Decorator to handle commit/rollback behavior within a database transaction."""
    @functools.wraps(func)
    def wrapper_func(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print('X connection failed')
            raise e
        finally: 
            conn.close()
    return wrapper_func


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
    

#### Update user's email with automatic transaction handling 
updated_user = update_user_email(user_id=1, new_email='Crawford_Cartwright@hoootmail.com')
print(updated_user)