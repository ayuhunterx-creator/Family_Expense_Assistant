from pathlib import Path
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
)
from .agent_team import build_team
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .monthly_report import make_report, show_report



BASE = Path(__file__).resolve().parents[2]


def main():
    team = build_team()

    session = SQLiteSession(
        "family_assistant_001",
        BASE / "data" / "chat_history.db",
    )

    print("家庭記帳小管家已啟動")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("exit", "結束"):
            break

        if not user_input:
            continue


        # ---------- 月報指令 ----------
        parts = user_input.split()

        if parts[0] == "/月報":
            if len(parts) == 1:
                month = datetime.now(
                    ZoneInfo("Asia/Taipei")
                ).strftime("%Y-%m")

            elif len(parts) == 2:
                month = parts[1]

            else:
                print("格式錯誤，請使用 /月報 YYYY-MM")
                continue

            if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
                print("月份格式錯誤，例如：/月報 2026-11")
                continue

            report = make_report(month, team)
            show_report(report)
            continue


        try:
            result = Runner.run_sync(
                team.front_desk,
                user_input,
                session=session,
            )

            print(f"\n回答的 Agent：{result.last_agent.name}")
            print(result.final_output)

        except InputGuardrailTripwireTriggered as error:
            check = error.guardrail_result.output.output_info

            print(
                "\n小管家：我只能協助家庭記帳、"
                "花費查詢、預算與省錢建議。"
            )
            print("阻擋原因：", check.reason)


if __name__ == "__main__":
    main()
