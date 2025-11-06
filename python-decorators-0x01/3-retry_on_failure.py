import time
import sqlite3 
import functools


#### paste your with_db_decorator here
db_connection = __import__('1-with_db_connection')
with_db_connection = db_connection.with_db_connection


def retry_on_failure(retries, delay):
    def wrapper(func):
        @functools.wraps(func)
        def wrapper_func(conn, *args, **kwargs):
            try:
                return func(conn, *args, **kwargs)
            except Exception as e:
                print(f"Initial attempt failed: {e}")
                for attempt in range(1, retries + 1):
                    print(f"Retrying ({attempt}/{retries}) after {delay}s...")
                    time.sleep(delay)
                    try:
                        new_conn = sqlite3.connect("users.db")
                        result = func(new_conn, *args, **kwargs)
                        new_conn.close()
                        return result
                    except Exception as retry_error:
                        print(f"Retry {attempt} failed: {retry_error}")
                        if attempt == retries:
                            raise retry_error
        return wrapper_func
    return wrapper

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)