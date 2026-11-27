import asyncio

import aiohttp
import aiosqlite


def make_future(value, delay_seconds=0.01):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    loop.call_later(delay_seconds, future.set_result, value)
    return future


def make_failing_future(error, delay_seconds=0.01):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    loop.call_later(delay_seconds, future.set_exception, error)
    return future


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            return response.status, await response.json()


async def create_users_table(db_path):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name TEXT NOT NULL, "
            "email TEXT NOT NULL UNIQUE)"
        )
        await db.commit()


async def add_user(db_path, name, email):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        await db.commit()
        return cursor.lastrowid


async def get_user(db_path, user_id):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return row


async def slow_square(number, delay_seconds=0.05):
    await asyncio.sleep(delay_seconds)
    return number * number


async def run_in_separate_thread(async_function, *args):
    return await asyncio.to_thread(asyncio.run, async_function(*args))
