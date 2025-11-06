import sqlite3



class DatabaseConnection:
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = None

    # initiating a database connection
    def __enter__(self):
        self.conn = sqlite3.connect(self.dbname)
        return self.conn

    #closing a database connection
    def __exit__(self, exc_type, exc_value, traceback):
         if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()



with DatabaseConnection('users.db') as dbconn:
    cursor = dbconn.cursor()
    cursor.execute("""SELECT * FROM users;""")
    users = cursor.fetchall()
    print(users)