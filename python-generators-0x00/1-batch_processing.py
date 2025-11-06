#!/usr/bin/env python3

import mysql.connector

from seed import connect_to_prodev


def stream_users_in_batches(batch_size):
    """
    Generator that streams rows from the user_data table one by one.
    Only one loop is used as required.
    """
    offset = 0
    connection = connect_to_prodev()
    if not connection:
        return 

    try:
        cursor = connection.cursor(dictionary=True)

        while True:
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")

            batch = cursor.fetchAll() 
            if not batch:
                break


            yield batch
            offset += batch_size

    except mysql.connector.Error as err:
        print(f"X Error streaming users: {err}")

    finally:
        cursor.close()
        connection.close()


def filter(age):
    def batch_processing(func):
        def wrapper_batch(*args, **kwargs):

            for batch in func(*args, **kwargs):
                for user in batch:
                    if user["age"] >= age:
                        yield user
        return wrapper_batch
    return batch_processing


@filter(25)
def stream_users_in_batches(batch_size):
    """
    Generator that streams rows from the user_data table one by one.
    Only one loop is used as required.
    """

    batch_buffer = []
    connection = connect_to_prodev()
    if not connection:
        return 

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data FETCH FIRST")

        for row in cursor:
            batch_buffer.append(row)
            if len(batch_buffer) == batch_size:
                yield batch_buffer
                batch_buffer = []


        if batch_buffer:
            yield batch_buffer

    except mysql.connector.Error as err:
        print(f"X Error streaming users: {err}")

    finally:
        cursor.close()
        connection.close()