import csv
from pathlib import Path
from datetime import date
from typing import Literal
from agents import function_tool

CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "expenses.csv"

Category = Literal[
    "餐飲",
    "交通",
    "日用品",
    "娛樂",
    "帳單",
    "其他"
]


# ---------- 共用 CSV 讀取函式 ----------
def read_expenses() -> list[dict]:
    """讀取所有帳目，並將金額轉換為整數。"""
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        expenses = list(csv.DictReader(f))

    for expense in expenses:
        expense["amount"] = int(expense["amount"])

    return expenses


def get_expenses(month: str | None = None) -> list[dict]:
    """讀取帳目，可依指定月份篩選。"""
    expenses = read_expenses()

    if month is None:
        return expenses

    return [
        expense
        for expense in expenses
        if expense["date"][:7] == month
    ]

# ---------- Agent 工具 ----------
@function_tool
def add_expense(
    item: str,
    amount: int,
    category: Category,
    member: str = "我",
    expense_date: str | None = None
) -> dict:
    """
    新增一筆消費紀錄至帳本。

    Args:
        item: 消費品項。
        amount: 消費金額，新台幣整數。
        category: 消費分類。
        member: 消費者，預設為我。
        expense_date: 消費日期，格式為 YYYY-MM-DD，未指定則使用今天。
    """
    
    # 1. 確認日期
    if expense_date is None:
        expense_date = date.today().isoformat()

    # 2. 整理成字典
    expense = {
        "date": expense_date,
        "member": member,
        "category": category,
        "item": item,
        "amount": amount
    }
    
     # 3. 寫入 CSV
    is_new_file = (
    not CSV_PATH.exists()
    or CSV_PATH.stat().st_size == 0
)

    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "member",
                "category",
                "item",
                "amount"
            ]
        )

        if is_new_file:
            writer.writeheader()

        writer.writerow(expense)
    # 4. 回傳新增的帳目
    return expense


@function_tool
def list_recent_expenses(n: int = 5) -> list[dict]:
    """
    列出帳本中最近 N 筆消費紀錄。

    Args:
        n: 查詢筆數，預設為5筆。
    """
     # 1. 檢查筆數
    if n <= 0:
        return []

    # 2. 讀取 CSV
    expenses = read_expenses()

    return expenses[-n:][::-1]


@function_tool
def delete_last_expense() -> dict:
    """
    刪除帳本中最後新增的一筆消費紀錄，
    並回傳被刪除的帳目。
    """

    expenses = read_expenses()

    if not expenses:
        return {"error": "帳本沒有任何紀錄"}

    deleted_expense = expenses.pop()

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "member", "category", "item", "amount"]
        )

        writer.writeheader()
        writer.writerows(expenses)
    
    
    return deleted_expense


@function_tool
def category_summary(month: str | None = None) -> dict:
    """統計各分類花費，可指定月份或統計全期間。

    Args:
        month: 指定月份 YYYY-MM，未提供則統計全期間。
    """
    categories = {
        "餐飲": 0,
        "交通": 0,
        "日用品": 0,
        "娛樂": 0,
        "帳單": 0,
        "其他": 0,
    }

    expenses = get_expenses(month)

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]
        categories[category] += amount

    return {
        "month": month,
        "categories": categories,
        "total": sum(categories.values()),
    }


@function_tool
def member_summary(month: str | None = None) -> dict:
    """統計家庭成員花費，可指定月份或統計全期間。

    Args:
        month: 指定月份 YYYY-MM，未提供則統計全期間。
    """
    members = {}
    expenses = get_expenses(month)

    for expense in expenses:
        member = expense["member"]
        amount = expense["amount"]

        if member not in members:
            members[member] = 0

        members[member] += amount

    return {
        "month": month,
        "members": members,
        "total": sum(members.values()),
    }


@function_tool
def monthly_member_summary(month: str) -> dict:
    """統計指定月份每位家庭成員的花費。

    Args:
        month: 指定月份，格式為 YYYY-MM。
    """
    members = {}

    expenses = read_expenses()

    for expense in expenses:
        if expense["date"][:7] == month:
            member = expense["member"]
            amount = expense["amount"]

            if member not in members:
                members[member] = 0

            members[member] += amount

    total = sum(members.values())

    return {
        "month": month,
        "members": members,
        "total": total,
    }


@function_tool
def calculate_budget(budget: int, spent: int) -> dict:
    """計算預算剩餘金額與超支狀態。

    Args:
        budget: 家規設定的預算金額。
        spent: 帳本統計的實際支出金額。
    """
    remaining = budget - spent

    return {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "is_over_budget": remaining < 0,
    }