import re
from copy import copy
from datetime import date
from pathlib import Path

import level_5 as team
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    input_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    InputGuardrailTripwireTriggered,
    TResponseInputItem,
)
from pydantic import BaseModel, Field

from common import MODEL
from prompts import get_instructions_with_date
from report_tools import MonthlyReport, build_monthly_report


# ---------- 路徑與 Session ----------
BASE = Path(__file__).resolve().parent
session = SQLiteSession(
    "family_level6_001",
    BASE / "data" / "chat_history.db"
)

# ---------- SavingCoach ----------
class SavingAdvice(BaseModel):
    advice: list[str] = Field(
        max_length=3,
        description="根據月報資料提出最多三項具體省錢建議"
    )


report_coach = copy(team.saving_coach_agent)
report_coach.tools = []
report_coach.output_type = SavingAdvice

report_coach.instructions = """
你是家庭記帳小管家的省錢教練。
根據使用者提供的月報資料，提出最多三項具體省錢建議。

規則：
1. 不需要重新查詢帳本。
2. 所有金額必須依照提供的月報資料，不可自行編造。
3. 建議須具體，盡量指出分類或消費項目。
4. 不可以推薦股票、基金、ETF 或其他投資標的。
5. 使用繁體中文回答。
"""

# ---------- ReportAgent ----------
report_agent = Agent(
    name="ReportAgent",
    model=MODEL,
    instructions="""
你是家庭記帳小管家的月報分析師。
根據提供的完整月報資料，輸出符合 MonthlyReport
結構的月報。

規則：
1. 所有金額必須依據提供的資料，不可編造。
2. 不得修改月份、總支出、分類、預算或最大單筆消費。
3. 必須保留全部六個分類。
4. 不得自行增加、刪除或修改 SavingCoach 的建議。
5. 使用指定的結構化輸出格式。
""",
    output_type=MonthlyReport,
)


# ---------- 月報執行流程 ----------
def make_report(month: str) -> MonthlyReport:
    """建立月報、取得省錢建議、驗證結構化輸出並儲存 JSON。"""

    # 1. Python 建立月報
    report = build_monthly_report(month)

    # 2. SavingCoach 提出建議
    coach_result = Runner.run_sync(
        report_coach,
        input=report.model_dump_json(indent=2)
    )

    # 只採用 SavingCoach 的建議
    report.advice = coach_result.final_output.advice

    # 3. ReportAgent 產生結構化月報
    result = Runner.run_sync(
        report_agent,
        input=(
            "請根據以下已驗證的月報資料輸出完整月報。"
            "不得修改任何欄位或數值。\n"
            + report.model_dump_json(indent=2)
        )
    )

    # 4. 檢查結構化輸出
    ai_report = result.final_output

    print("ReportAgent 輸出型態：", type(ai_report))

    if not isinstance(ai_report, MonthlyReport):
        raise TypeError("ReportAgent 未回傳 MonthlyReport")

    # 5. 保留 Python 建立的原始月報
    # 不採用 AI 重新產生的金額或分類

    # 6. 儲存 JSON
    output_path = BASE / "data" / f"report_{month}.json"

    output_path.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8"
    )

    print("月報已儲存：", output_path)

    return report


# ---------- Input Guardrail ----------
class TopicCheck(BaseModel):
    on_topic: bool = Field(description="最後一句話是否屬於家庭記帳、花費、預算的服務範圍")
    asks_investment: bool = Field(description="是否在要求推薦或評價股票、基金、ETF、加密貨幣等投資標的")
    reason: str = Field(description="一句話說明判斷理由")


topic_checker = Agent(
    name="TopicGuard",
    model=MODEL,
    instructions="""
你是家庭記帳小管家的輸入安全檢查員。
只判斷使用者最新的輸入，不回答問題。

判斷規則：
1. 記帳、支出查詢、預算、儲蓄、省錢建議應放行。
2. 無關的閒聊、作業或其他問題應阻擋。
3. 要求推薦、挑選或評價股票、基金、ETF、
   加密貨幣等投資標的，一律設定 asks_investment=True。
4. 即使問題涉及家庭預算，只要要求推薦投資標的，
   仍必須阻擋。
5. 一般記帳中的股票交易費用紀錄，不等於要求投資推薦。
6. 使用繁體中文提供簡短判斷理由。
""",
    output_type=TopicCheck,
)

@input_guardrail(run_in_parallel=False)
async def topic_guard(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """檢查使用者輸入是否符合家庭記帳服務範圍。"""

    result = await Runner.run(
        topic_checker,
        input,
        context=ctx.context,
    )

    check = result.final_output

    blocked = (
        not check.on_topic
        or check.asks_investment
    )

    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=blocked,
    )

# 註冊護欄：必須放在 topic_guard 定義之後
team.front_desk_agent.input_guardrails = [topic_guard]


# ---------- 更新 Agent 日期 ----------
def update_agent_dates():
    """每輪重新設定 Agent instructions 的日期。"""

    team.accountant_agent.instructions = get_instructions_with_date(
        team.ACCOUNTANT_INSTRUCTIONS
    )
    team.analyst_agent.instructions = get_instructions_with_date(
        team.ANALYST_INSTRUCTIONS
    )
    team.budget_agent.instructions = get_instructions_with_date(
        team.BUDGET_INSTRUCTIONS
    )
    team.saving_coach_agent.instructions = get_instructions_with_date(
        team.SAVING_COACH_INSTRUCTIONS
    )
    team.front_desk_agent.instructions = get_instructions_with_date(
        team.FRONT_DESK_INSTRUCTIONS
    )



# ---------- 顯示月報 ----------
def show_report(report: MonthlyReport):
    print(f"\n【月報員】{report.month}")
    print(f"總支出：{report.total:,} 元")

    print("\n六分類支出：")

    for line in report.lines:
        print(
            f"{line.category}："
            f"已花 {line.spent:,} 元 / "
            f"預算 {line.budget:,} 元 / "
            f"超支：{line.is_over_budget}"
        )

    print("\n最大單筆消費：")

    if report.biggest_item:
        print(
            f"{report.biggest_item.item}："
            f"{report.biggest_item.amount:,} 元"
        )
    else:
        print("本月沒有消費紀錄")

    print("\n省錢建議：")

    for advice in report.advice:
        print("-", advice)


# ---------- 主程式 ----------
def main():

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("exit", "結束"):
            break

        if not user_input:
            continue

        # 月報指令
        parts = user_input.split()

        if parts[0] == "/月報":

            if len(parts) == 1:
                month = date.today().strftime("%Y-%m")

            elif len(parts) == 2:
                month = parts[1]

            else:
                print("格式錯誤，請使用 /月報 YYYY-MM")
                continue

            if not re.fullmatch(
                r"\d{4}-(0[1-9]|1[0-2])", month
            ):
                print("月份格式錯誤，例如：/月報 2026-11")
                continue

            report = make_report(month)
            show_report(report)

        # 一般問題交給 FrontDesk
        else:
            update_agent_dates()

            try:
                result = Runner.run_sync(
                    team.front_desk_agent,
                    user_input,
                    session=session,
                )

                print("回答的 Agent：", result.last_agent.name)
                print(result.final_output)

            except InputGuardrailTripwireTriggered as error:
                check = error.guardrail_result.output.output_info

                print(
                    "小管家：我只能協助家庭記帳、"
                    "花費查詢、預算與省錢建議。"
                )
                print("阻擋原因：", check.reason)


if __name__ == "__main__":
    main()