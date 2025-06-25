from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import date
from typing import Optional

from app.models.models import TransactionCreate, TransactionInDB, UserInDB
from app.auth.auth import get_current_active_user
from app.data.database import get_db_connection

router = APIRouter()

@router.post("/transactions/", response_model=TransactionInDB)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    transaction_id = str(uuid.uuid4())
    try:
        cursor.execute(
            "INSERT INTO transactions (id, user_id, date, amount, type, category, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                transaction_id,
                current_user.id,
                transaction.date.isoformat(),
                transaction.amount,
                transaction.type,
                transaction.category,
                transaction.description,
            ),
        )
        conn.commit()
        return TransactionInDB(
            id=transaction_id,
            user_id=current_user.id,
            date=transaction.date,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            description=transaction.description,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()

@router.get("/transactions/", response_model=List[TransactionInDB])
async def read_transactions(
    current_user: UserInDB = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, user_id, date, amount, type, category, description FROM transactions WHERE user_id = ?"
    params = [current_user.id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date.isoformat())
    if end_date:
        query += " AND date <= ?"
        params.append(end_date.isoformat())

    cursor.execute(query, params)
    transactions_data = cursor.fetchall()
    conn.close()
    return [TransactionInDB(**t) for t in transactions_data]

@router.get("/transactions/{transaction_id}", response_model=TransactionInDB)
async def read_transaction(
    transaction_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, date, amount, type, category, description FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, current_user.id),
    )
    transaction_data = cursor.fetchone()
    conn.close()
    if not transaction_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionInDB(**transaction_data)

@router.put("/transactions/{transaction_id}", response_model=TransactionInDB)
async def update_transaction(
    transaction_id: str,
    transaction: TransactionCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET date = ?, amount = ?, type = ?, category = ?, description = ? WHERE id = ? AND user_id = ?",
        (
            transaction.date.isoformat(),
            transaction.amount,
            transaction.type,
            transaction.category,
            transaction.description,
            transaction_id,
            current_user.id,
        ),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    conn.close()
    return TransactionInDB(
        id=transaction_id,
        user_id=current_user.id,
        date=transaction.date,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        description=transaction.description,
    )

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, current_user.id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    conn.close()
    return