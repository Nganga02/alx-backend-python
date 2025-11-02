#!/usr/bin/env python3

import mysql.connector

from seed import connect_to_prodev


def stream_users():
    """
    Generator that streams rows from the user_data table one by one.
    Only one loop is used as required.
    """
    connection = connect_to_prodev()
    if not connection:
        return 

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

      
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"X Error streaming users: {err}")

    finally:
        cursor.close()
        connection.close()
