from agents import (
    Agent,
    Runner,
    input_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
)
from pydantic import BaseModel, Field
from common import MODEL



# ---------- 輸入檢查結果 ----------
class TopicCheck(BaseModel):
    on_topic: bool = Field(description="最後一句話是否屬於家庭記帳、花費、預算的服務範圍")
    asks_investment: bool = Field(description="是否在要求推薦或評價股票、基金、ETF、加密貨幣等投資標的")
    reason: str = Field(description="一句話說明判斷理由")


# ---------- 輸入檢查 Agent ----------
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


# ---------- Input Guardrail ----------
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
