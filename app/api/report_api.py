from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date
from collections import defaultdict

from app.models.models import ReportSummary, UserInDB
from app.auth.auth import get_current_active_user
from app.data.database import get_db_connection

router = APIRouter()

@router.get("/reports/summary", response_model=ReportSummary)
async def get_financial_summary(
    current_user: UserInDB = Depends(get_current_active_user),
    start_date: date = None,
    end_date: date = None,
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT amount, type, category FROM transactions WHERE user_id = ?"
    params = [current_user.id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date.isoformat())
    if end_date:
        query += " AND date <= ?"
        params.append(end_date.isoformat())

    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()

    total_income = 0.0
    total_expenses = 0.0
    spending_by_category = defaultdict(float)
    income_by_category = defaultdict(float)

    for t in transactions:
        if t['type'] == 'income':
            total_income += t['amount']
            income_by_category[t['category']] += t['amount']
        elif t['type'] == 'expense':
            total_expenses += t['amount']
            spending_by_category[t['category']] += t['amount']

    net_balance = total_income - total_expenses

    return ReportSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        spending_by_category=spending_by_category,
        income_by_category=income_by_category,
    )