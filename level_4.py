from common import MODEL
from prompts import LEVEL_4_INSTRUCTIONS, get_instructions_with_date
from agents import Agent, Runner, ModelSettings
from agents import SQLiteSession
from rules_tools import search_house_rules
from pathlib import Path
from expense_tools import (
    add_expense,
    list_recent_expenses,
    delete_last_expense,
    monthly_summary,
    member_summary
)

# ===== Agent 設定 =====

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

# ===== 對話記憶 =====

DB_PATH = Path(__file__).resolve().parent / "data" / "chat_history.db"

session = SQLiteSession("family_001", DB_PATH)

# ===== 主程式 =====

def main():
    while True:
        user_input = input("You: ")

        if user_input in ("結束", "exit"):
            break

        agent.instructions = get_instructions_with_date(
            LEVEL_4_INSTRUCTIONS
        )

        result = Runner.run_sync(
            agent,
            user_input,
            session=session
        )

        print(result.final_output)


if __name__ == "__main__":
    main()
