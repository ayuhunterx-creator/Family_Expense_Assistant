from pathlib import Path
from agents import Runner
from agent_team import AgentTeam
from report_tools import MonthlyReport, build_monthly_report

BASE = Path(__file__).resolve().parent


def make_report(month: str, team: AgentTeam) -> MonthlyReport:
    report = build_monthly_report(month)

    result = Runner.run_sync(
        team.report_agent,
        input=report.model_dump_json(indent=2),
    )

    ai_report = result.final_output
    if not isinstance(ai_report, MonthlyReport):
        raise TypeError("ReportAgent 未回傳 MonthlyReport")

    # 只採用 AI 的省錢建議
    report.advice = ai_report.advice[:3]

    # 保留 Python 計算的所有數字
    output_path = BASE / "data" / f"report_{month}.json"

    output_path.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print("月報已儲存：", output_path)
    
    return report


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