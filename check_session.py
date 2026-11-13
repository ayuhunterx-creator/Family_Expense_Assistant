import asyncio
import json
from pathlib import Path
from agents import SQLiteSession

DB_PATH = Path(__file__).resolve().parent / "data" / "chat_history.db"

session = SQLiteSession("family_debug", DB_PATH)


async def main():
    items = await session.get_items()

    print(json.dumps(
        items,
        ensure_ascii=False,
        indent=4
    ))


asyncio.run(main())