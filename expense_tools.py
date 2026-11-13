import csv
import json
from pathlib import Path
from datetime import date
from typing import Literal
from agents import function_tool

CSV_PATH = Path(__file__).resolve().parent / "data" / "expenses.csv"

Category = Literal[
    "餐飲",
    "交通",
    "日用品",
    "娛樂",
    "帳單",
    "其他"
]


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
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expenses = list(reader)

    # 3. 將金額轉換成整數
    for expense in expenses:
        expense["amount"] = int(expense["amount"])

    # 4. 取出最後 N 筆，最新的排在最前面
    return expenses[-n:][::-1]


@function_tool
def delete_last_expense() -> dict:
    """
    刪除帳本中最後新增的一筆消費紀錄，
    並回傳被刪除的帳目。
    """

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expenses = list(reader)

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
    
    deleted_expense["amount"] = int(deleted_expense["amount"])
    
    return deleted_expense


@function_tool
def monthly_summary(month: str) -> dict:
    """
    統計指定月份的各分類花費及總金額。

    Args:
        month: 指定月份，格式為 YYYY-MM。
    """

    categories = {
    "餐飲": 0,
    "交通": 0,
    "日用品": 0,
    "娛樂": 0,
    "帳單": 0,
    "其他": 0
}

    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expenses = list(reader)

        # 只有符合指定月份的帳目才進行統計
    for expense in expenses:
        if expense["date"][:7] == month:
            category = expense["category"]
            amount = int(expense["amount"])
            categories[category] += amount

    total = sum(categories.values())

    return {
        "month": month,
        "categories": categories,
        "total": total
    }


@function_tool
def member_summary() -> dict:
    """
    統計帳本中每位家庭成員的全期間累計花費。
    不支援依月份或日期篩選。
    """
    # 1. 建立空字典
    members = {}

    # 2. 讀取 CSV
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expenses = list(reader)

    # 3. 統計每位成員的花費
    for expense in expenses:
        member = expense["member"]
        amount = int(expense["amount"])

        if member not in members:
            members[member] = 0

        members[member] += amount

    # 4. 計算家庭總花費
    total = sum(members.values())

    # 5. 回傳結果
    return {
        "members": members,
        "total": total
    }


