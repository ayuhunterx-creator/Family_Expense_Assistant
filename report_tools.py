from pydantic import BaseModel, Field, ConfigDict
from expense_tools import get_expenses, Category
from pathlib import Path

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


RULES_PATH = Path(__file__).resolve().parent / "data" / "house_rules.md"

def read_house_rules() -> str:
    """讀取家庭家規 Markdown 文件。"""
    return RULES_PATH.read_text(encoding="utf-8")


def get_category_budgets() -> dict[str, int]:
    """從家規文件取得六分類預算。"""
    rules_text = read_house_rules()
    budgets = {}

    # 只取得「每月預算」章節
    budget_section = rules_text.split("## 一、每月預算", 1)[1]
    budget_section = budget_section.split("## 二、", 1)[0]

    for line in budget_section.splitlines():
        if not line.startswith("|"):
            continue

        parts = line.split("|")
        category = parts[1].strip()
        amount = parts[2].strip().replace(",", "")

        # 排除表格標題及分隔線
        if category not in ["餐飲", "交通", "日用品", "娛樂", "帳單", "其他"]:
            continue

        budgets[category] = int(amount)

    # 確認六分類完整
    categories = {"餐飲", "交通", "日用品", "娛樂", "帳單", "其他"}

    if set(budgets) != categories:
        raise ValueError("家規預算分類不完整")

    if any(amount < 0 for amount in budgets.values()):
        raise ValueError("預算不可為負數")

    return budgets


class ReportLine(BaseModel):
    category: Category = Field(description="分類名稱：餐飲、交通、日用品、娛樂、帳單、其他")
    spent: int = Field(description="該分類本月已花金額，來自 category_summary")
    budget: int = Field(description="家規規定的每月預算，來自 get_category_budgets，不可自行編造")
    is_over_budget: bool = Field(description="已花金額是否超過預算，由 Python 計算")


class MonthlyReport(BaseModel):
    month: str = Field(description="月份 YYYY-MM")
    total: int = Field(description="本月總花費（整數）")
    lines: list[ReportLine] = Field(description="六個分類的支出與預算明細")
    biggest_item: BiggestExpense | None = Field(description="本月最大筆的花費，來自 get_biggest_expense；無消費紀錄時為 null")
    advice: list[str] = Field(max_length=3,description="根據實際消費資料提出最多三項具體省錢建議")
