import json
import os
from agents import function_tool,FileSearchTool
from datetime import date
from common import MODEL, VECTOR_STORE_ID
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
from common import MODEL, VECTOR_STORE_ID

if not VECTOR_STORE_ID:
    raise RuntimeError(
        "請在 .env 設定 VECTOR_STORE_ID"
    )

house_rules_tool = FileSearchTool(
    vector_store_ids=[VECTOR_STORE_ID]
)

rules_agent = Agent(
    name="家規搜尋助手",
    model=MODEL,
    instructions="""
    使用 FileSearchTool 搜尋家規文件，
    依照搜尋結果回答問題，不可自行編造家規。
    """,
    tools=[house_rules_tool],
    model_settings=ModelSettings(
        tool_choice="required",
        parallel_tool_calls=False
    )
)

@function_tool
async def search_house_rules(question: str) -> str:
    """
    搜尋家規文件，回答預算、零用錢及消費規則問題。

    Args:
        question: 需要查閱家規的問題。
    """

    confirm = input(
        "\n需要搜尋家規，是否允許？(y/n): "
    ).strip().lower()

    if confirm != "y":
        return "使用者取消搜尋，不可編造家規。"

    result = await Runner.run(
        rules_agent,
        question
    )

    return result.final_output

agent = Agent(
    name="家庭記帳小管家",
    model=MODEL,
    instructions=LEVEL_4_INSTRUCTIONS,
    tools=[
        add_expense,
        list_recent_expenses,
        delete_last_expense,
        monthly_summary,
        member_summary,
        search_house_rules
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
    print(result.final_output)
