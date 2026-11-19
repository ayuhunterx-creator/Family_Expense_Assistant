from .common import MODEL
from dataclasses import dataclass
from agents import Agent
from .guardrails import topic_guard
from .rules_tools import search_house_rules
from .report_tools import MonthlyReport
from . import expense_tools
from .prompts import (
    get_instructions_with_date,
    ACCOUNTANT_INSTRUCTIONS,
    ANALYST_INSTRUCTIONS,
    BUDGET_INSTRUCTIONS,
    SAVING_COACH_INSTRUCTIONS,
    FRONT_DESK_INSTRUCTIONS,
    REPORT_INSTRUCTIONS,
)

# ---------- 團隊 ----------
@dataclass
class AgentTeam:
    front_desk: Agent
    accountant: Agent
    analyst: Agent
    budget_manager: Agent
    saving_coach: Agent
    report_agent: Agent


def build_team() -> AgentTeam:
    

    accountant_agent = Agent(
    name="Accountant",
    model=MODEL,
    instructions=get_instructions_with_date(ACCOUNTANT_INSTRUCTIONS),
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
    instructions=get_instructions_with_date(ANALYST_INSTRUCTIONS),
    handoff_description="處理每月花費、分類統計、家庭成員消費比較等分析需求。",
    tools=[
        expense_tools.category_summary,
        expense_tools.member_summary,
    ],
)

    budget_agent = Agent(
        name="BudgetManager",
        model=MODEL,
        instructions=get_instructions_with_date(BUDGET_INSTRUCTIONS),
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
        instructions=get_instructions_with_date(SAVING_COACH_INSTRUCTIONS),
        handoff_description="處理省錢方法、節省開銷、改善消費習慣等建議需求。",
        tools=[
            expense_tools.category_summary,
            expense_tools.member_summary,
        ],
    )

    report_agent = Agent(
    name="ReportAgent",
    model=MODEL,
    instructions=get_instructions_with_date(REPORT_INSTRUCTIONS),
    output_type=MonthlyReport,
)

    front_desk_agent = Agent(
    name="FrontDesk",
    model=MODEL,
    instructions=get_instructions_with_date(FRONT_DESK_INSTRUCTIONS),

    handoffs=[
        accountant_agent, 
        analyst_agent, 
        budget_agent, 
        saving_coach_agent],
    input_guardrails=[topic_guard],
)


    return AgentTeam(
        front_desk=front_desk_agent,
        accountant=accountant_agent,
        analyst=analyst_agent,
        budget_manager=budget_agent,
        saving_coach=saving_coach_agent,
        report_agent=report_agent,
    )



