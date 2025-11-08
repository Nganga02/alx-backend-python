import aiosqlite
import asyncio



async def async_fetch_users() -> list:
    async with aiosqlite.connect('users.db') as db_conn:
        async with db_conn.execute("""SELECT * FROM users""") as cursor:
            results = await cursor.fetchall()

    return results

async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db_conn:
        async with db_conn.execute("""SELECT * FROM users WHERE age > 40""") as cursor:
            results = await cursor.fetchall()
    return results


async def fetch_concurrently():
    tasks = [asyncio.create_task(async_fetch_users()), asyncio.create_task(async_fetch_older_users())]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(results)

asyncio.run(fetch_concurrently())
    