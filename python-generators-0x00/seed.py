from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import errorcode
import csv
import uuid



# loading db config 
load_dotenv()


def connect_db():
    try:
        connection = mysql.connector.connect(
            host= os.getenv("HOST"),
            user=os.getenv("DB_USER"),          
            password=os.getenv("DB_PASSWORD")  
        )
        print("\u2713 Connected to MySQL server.")
        return connection
    except mysql.connector.Error as err:
        print(f"X Error connecting to MySQL: {err}")
        return None


def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("\u2713 Database 'ALX_prodev' ready.")
    except mysql.connector.Error as err:
        print(f"X Failed creating database: {err}")


def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host= os.getenv("HOST"),
            user=os.getenv("DB_USER"),          
            password=os.getenv("DB_PASSWORD"),  
            database="ALX_prodev"
        )
        print("\u2713 Connected to ALX_prodev database.")
        return connection
    except mysql.connector.Error as err:
        print(f"X Error connecting to ALX_prodev: {err}")
        return None


def create_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(3,0) NOT NULL,
        INDEX (user_id)
    )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("\u2713 Table 'user_data' is ready.")
    except mysql.connector.Error as err:
        print(f"X Failed creating table: {err}")


def insert_data(connection, data_file):

    insert_query = """
        INSERT IGNORE INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor = connection.cursor()
        inserted_count = 0
        
        with open(data_file, 'r') as userfile:
            reader = csv.DictReader(userfile)
            

            for row in reader:
                user = (
                    str(uuid.uuid4()),
                    row['name'],
                    row["email"],
                    row["age"]
                )
            
                cursor.execute(insert_query, user)
                inserted_count += cursor.rowcount
        connection.commit()

        print(f"\u2713 Inserted {cursor.rowcount} new rows successfully.")

    except mysql.connector.Error as err:
        print(f"X Error inserting data: {err}")

    finally:
        cursor.close()




