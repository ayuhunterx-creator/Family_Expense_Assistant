from pydantic import BaseModel, Field, ConfigDict
from expense_tools import get_expenses, Category

# ---------- 工具 ----------
def get_monthly_expenses(month: str) -> list[dict]:
    """取得指定月份的所有消費紀錄。"""
    expenses = read_expenses()

    return [
        expense
        for expense in expenses
        if expense["date"][:7] == month
    ]

def get_biggest_expense(month: str) -> dict | None:
    """取得指定月份金額最高的單筆消費。"""
    expenses = get_expenses(month)

    if not expenses:
        return None

    return max(expenses, key=lambda expense: expense["amount"])


class ReportLine(BaseModel):
    category: Category
    spent: int
    budget: int
    is_over_budget: bool

class BiggestExpense(BaseModel):
    date: str
    member: str
    category: Category
    item: str
    amount: int

class MonthlyReport(BaseModel):
    month: str
    total: int
    lines: list[ReportLine]
    biggest_item: BiggestExpense | None
    advice: list[str] = Field(max_length=3)
