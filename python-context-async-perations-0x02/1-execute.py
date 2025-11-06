import sqlite3


class ExecuteQuery:
    def __init__(self, dbname, query):
        self.db = dbname
        self.query = query
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db)
        cursor = self.conn.cursor()
        cursor.execute(self.query)
        results = cursor.fetchall()
        return results
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()


with ExecuteQuery('users.db', """SELECT * FROM users;""") as users:
    print(users)
