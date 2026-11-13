import json
from datetime import date
from common import MODEL
from prompts import LEVEL_4_INSTRUCTIONS
from agents import Agent, Runner, ModelSettings
from agents import ToolCallItem, ToolCallOutputItem
from agents import SQLiteSession
from pathlib import Path
from expense_tools import (
    add_expense,
    list_recent_expenses,
    delete_last_expense,
    monthly_summary,
    member_summary
)


agent = Agent(
    name="家庭記帳小管家",
    model=MODEL,
    instructions=LEVEL_4_INSTRUCTIONS,
    tools=[
        add_expense,
        list_recent_expenses,
        delete_last_expense,
        monthly_summary,
        member_summary
    ],
    model_settings=ModelSettings(
        parallel_tool_calls=False
    )
)

DB_PATH = Path(__file__).resolve().parent / "data" / "chat_history.db"

session = SQLiteSession("family_001", DB_PATH)

# ===== 測試區 =====

while True:
    user_input = input("You: ")

    if user_input == "結束":
        break

    # 每次執行前更新今天日期
    agent.instructions = (
        LEVEL_4_INSTRUCTIONS
        + f"\n今天日期是 {date.today().isoformat()}。"
    )

    result = Runner.run_sync(
    agent,
    user_input,
    session=session
)