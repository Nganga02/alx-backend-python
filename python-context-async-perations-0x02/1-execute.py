import sqlite3


class ExecuteQuery:
    def __init__(self, dbname, query, parameters = None):
        self.db = dbname
        self.query = query
        self.conn = None
        self.params = parameters or ()
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        cursor = self.conn.cursor()
        cursor.execute(self.query,self.params)
        results = cursor.fetchall()
        return results
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

query = """SELECT * FROM users WHERE age > ?;"""
with ExecuteQuery('users.db', query, parameters=(25,)) as users:
    print(users)
