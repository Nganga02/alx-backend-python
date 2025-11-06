import time
import sqlite3 
import functools

#### paste your with_db_decorator here
db_connection = __import__('1-with_db_connection')
with_db_connection = db_connection.with_db_connection

query_cache = {}
def cache_query(func):
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        query = kwargs.get('query') or (args[1] if args else None)
        if query in query_cache.keys():
            print("This is from the cached data")
            return query_cache[query]
        else:
            try:
                print("this is from the first query and the data is cached")
                result = func(*args, **kwargs)
                query_cache.update({query:result})
                return result
            except Exception as e:
                raise e
    return wrapper_func
        

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

time.sleep(3)

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")