

users_stream = __import__('0-stream_users')

def stream_user_ages():
    for user in users_stream.stream_users():
        yield user["age"]



def users_avg_age():
    users = 1 
    total = 0
    for age in stream_user_ages():
        total += age
        users += 1
    yield total/users