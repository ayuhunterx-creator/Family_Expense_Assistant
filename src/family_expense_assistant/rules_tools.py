from agents import Agent, Runner, FileSearchTool, ModelSettings, function_tool
from .common import MODEL, VECTOR_STORE_ID

if not VECTOR_STORE_ID:
    raise RuntimeError("請在 .env 設定 VECTOR_STORE_ID")


rules_agent = Agent(
    name="RulesAssistant",
    model=MODEL,
    instructions="使用 FileSearchTool 搜尋家規文件，依照搜尋結果回答，不可編造家規。",
    tools=[FileSearchTool(vector_store_ids=[VECTOR_STORE_ID])],
    model_settings=ModelSettings(
        tool_choice="required",
        parallel_tool_calls=False,
    ),
)

@function_tool
async def search_house_rules(question: str) -> str:
    """搜尋家規文件，回答預算、零用錢及消費規則問題。"""

    result = await Runner.run(rules_agent, question)
    return result.final_output