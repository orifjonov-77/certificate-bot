import asyncio
import os
import aiosqlite

DB_PATH = r"C:\Users\777 comp service\Desktop\certificate\data\database.db"

async def check():
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("PRAGMA table_info(certificates)") as cursor:
            cols = await cursor.fetchall()
            print("certificates ustunlari:", [c["name"] for c in cols])
        async with db.execute("SELECT * FROM test_results ORDER BY id DESC LIMIT 5") as cursor:
            rows = await cursor.fetchall()
            print(f"Jami natijalar ({len(rows)} ta):")
            for r in rows:
                print(dict(r))

asyncio.run(check())
