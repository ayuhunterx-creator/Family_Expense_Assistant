import expense_tools
from agents import Agent, Runner
from agents import SQLiteSession
from rules_tools import search_house_rules
from common import MODEL
from pathlib import Path
from prompts import get_instructions_with_date
from agents import ToolCallItem, ToolCallOutputItem, HandoffCallItem


accountant_agent = Agent(
    name="Accountant",
    model=MODEL,
    instructions="""你是記帳員，負責新增、查看及刪除帳目。
所有帳目操作必須呼叫對應工具。
只有工具確認成功後，才能告知使用者操作完成。""",
    handoff_description="處理新增、查看或刪除個別消費紀錄的需求。",
    tools=[
        expense_tools.add_expense,
        expense_tools.list_recent_expenses,
        expense_tools.delete_last_expense,
    ],
)

analyst_agent = Agent(
    name="Analyst",
    model=MODEL,
    instructions="""你是分析師，負責統計與比較家庭花費。
所有統計數字必須來自工具，不可自行編造。
分類統計使用 category_summary。
家庭成員統計使用 member_summary。
需要指定月份時，傳入 YYYY-MM；全期間統計不傳月份。
完成分析後，提供一句簡短觀察。""",
    handoff_description="處理每月花費、分類統計、家庭成員消費比較等分析需求。",
    tools=[
        expense_tools.category_summary,
        expense_tools.member_summary,
    ],
)

budget_agent = Agent(
    name="BudgetManager",
    model=MODEL,
    instructions="""你是家庭預算管家，負責家庭預算、零用錢、大筆消費及家規問題。
工具使用規則：
1. 涉及家規時，必須呼叫 search_house_rules；使用者取消搜尋時，不得推測或編造家規。
2. 涉及實際支出時，必須呼叫 category_summary，不得編造帳本金額。
3. 計算剩餘預算或超支情況時，依序執行：
   - search_house_rules：取得家規預算。
   - category_summary：取得指定月份的實際支出。
   - calculate_budget：計算剩餘金額與超支狀態。

回答規則：
1. 準確區分家規中的「討論」與「核准」，不得自行提高限制。
2. 回答預算餘額時，列出月份、分類、預算金額、已支出金額、剩餘金額及超支狀態。
3. 所有金額與規則必須依據工具結果，不得自行編造。
4. 未查詢帳本前，不得宣稱沒有支出。
5. 工具查詢失敗或缺少必要資料時，應說明無法確認，不得自行推算。""",
    handoff_description="處理預算、零用錢、大筆消費及家規相關需求。",
    tools=[
        search_house_rules,
        expense_tools.category_summary,
        expense_tools.calculate_budget,
    ],
)


saving_coach_agent = Agent(
    name="SavingCoach",
    model=MODEL,
    instructions="""你是家庭省錢教練。
根據實際消費資料，提供具體可行的省錢建議。
分析消費分類時使用 category_summary。
分析家庭成員支出時使用 member_summary。
需要指定月份時，傳入 YYYY-MM；全期間統計不傳月份。
所有金額必須來自工具，不可自行編造。
每次最多提供三項具體省錢建議。
不負責新增、修改、刪除帳目，也不負責核准消費。""",
    handoff_description="處理省錢方法、節省開銷、改善消費習慣等建議需求。",
    tools=[
        expense_tools.category_summary,
        expense_tools.member_summary,
    ],
)


front_desk_agent = Agent(
    name="FrontDesk",
    model=MODEL,
    instructions="""你是家庭記帳小管家的櫃台。
只負責判斷使用者需求並轉交適合的專家。
不可自行回答。""",
    handoffs=[
        accountant_agent, 
        analyst_agent, 
        budget_agent, 
        saving_coach_agent]
)


# ===== 對話記憶 =====

DB_PATH = Path(__file__).resolve().parent / "data" / "chat_history.db"

session = SQLiteSession("family_level5_001", DB_PATH)

# 保存原本的 instructions
FRONT_DESK_INSTRUCTIONS = front_desk_agent.instructions
ACCOUNTANT_INSTRUCTIONS = accountant_agent.instructions
ANALYST_INSTRUCTIONS = analyst_agent.instructions
BUDGET_INSTRUCTIONS = budget_agent.instructions
SAVING_COACH_INSTRUCTIONS = saving_coach_agent.instructions

# ===== 主程式 =====

def main():

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("結束", "exit"):
            break

        accountant_agent.instructions = get_instructions_with_date(ACCOUNTANT_INSTRUCTIONS)
        analyst_agent.instructions = get_instructions_with_date(ANALYST_INSTRUCTIONS)
        budget_agent.instructions = get_instructions_with_date(BUDGET_INSTRUCTIONS)
        saving_coach_agent.instructions = get_instructions_with_date(SAVING_COACH_INSTRUCTIONS)
        front_desk_agent.instructions = get_instructions_with_date(FRONT_DESK_INSTRUCTIONS)

        result = Runner.run_sync(
            front_desk_agent,
            user_input,
            session=session
        )

        # for item in result.new_items:
        #     if isinstance(item, ToolCallItem):
        #         print("呼叫工具：", getattr(item.raw_item, "name", "內建工具"))

        #     elif isinstance(item, ToolCallOutputItem):
        #         print("工具回傳：", item.output)

        #     elif isinstance(item, HandoffCallItem):
        #         print("Handoff：", item.raw_item.name)

        print("回答的 Agent：", result.last_agent.name)
        print(result.final_output)


if __name__ == "__main__":
    main()