import asyncpg
from asyncpg import Record
from typing import List
from secure_data import PG_HOST, PG_PORT, PG_USER, PG_DB, PG_PASSWORD


async def connect():
    return await asyncpg.connect(host=PG_HOST,
                          port=PG_PORT,
                          user=PG_USER,
                          database=PG_DB,
                          password=PG_PASSWORD)


async def select_from_bd(connection, title:str, artist:str):
    SELECT = f"SELECT * FROM audio WHERE title=\'{title}\' AND artist=\'{artist}\'"
    results: List[Record] = await connection.fetch(SELECT)
    return results


async def insert_into_bd(connection, title:str, artist:str, path: str):
    INSERT = f"INSERT INTO audio (title, artist, path) VALUES (\'{title}\', \'{artist}\', \'{path}\')"

    await connection.execute(INSERT)