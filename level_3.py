import json
from datetime import date
from common import MODEL
from prompts import LEVEL_3_INSTRUCTIONS, get_instructions_with_date
from agents import Agent, Runner, ModelSettings
from agents import ToolCallItem, ToolCallOutputItem
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
    instructions=LEVEL_3_INSTRUCTIONS,
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

# ===== 測試區 =====

while True:
    user_input = input("You: ")

    if user_input in ("結束", "exit"):
        break

    # 每次執行前更新今天日期
    agent.instructions = get_instructions_with_date(LEVEL_3_INSTRUCTIONS)

    result = Runner.run_sync(agent, user_input)

    # for item in result.new_items:
    #     if isinstance(item, ToolCallItem):
    #         print("呼叫工具：", item.raw_item.name)
    #         print("工具參數：", item.raw_item.arguments)
    #     elif isinstance(item, ToolCallOutputItem):
    #         print("工具結果：", item.output)

    print(result.final_output)

    # usage = result.context_wrapper.usage
    # print("Total tokens:", usage.total_tokens)
    # print("API requests:", usage.requests)