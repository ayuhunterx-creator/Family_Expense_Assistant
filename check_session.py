import asyncio
import json
from pathlib import Path
from agents import SQLiteSession

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "data" / "chat_history.db"


async def main():
    session = SQLiteSession(
        "family_assistant_001",
        DB_PATH,
    )

    items = await session.get_items()

    print(json.dumps(
        items,
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    asyncio.run(main())