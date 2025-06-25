from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import date

from app.models.models import RecurringTransactionCreate, RecurringTransactionInDB, UserInDB
from app.auth.auth import get_current_active_user
from app.data.database import get_db_connection

router = APIRouter()

@router.post("/recurring-transactions/", response_model=RecurringTransactionInDB)
async def create_recurring_transaction(
    recurring_transaction: RecurringTransactionCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    recurring_transaction_id = str(uuid.uuid4())
    try:
        cursor.execute(
            "INSERT INTO recurring_transactions (id, user_id, name, amount, type, category, description, frequency, start_date, next_due_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                recurring_transaction_id,
                current_user.id,
                recurring_transaction.name,
                recurring_transaction.amount,
                recurring_transaction.type,
                recurring_transaction.category,
                recurring_transaction.description,
                recurring_transaction.frequency,
                recurring_transaction.start_date.isoformat(),
                recurring_transaction.next_due_date.isoformat(),
            ),
        )
        conn.commit()
        return RecurringTransactionInDB(
            id=recurring_transaction_id,
            user_id=current_user.id,
            name=recurring_transaction.name,
            amount=recurring_transaction.amount,
            type=recurring_transaction.type,
            category=recurring_transaction.category,
            description=recurring_transaction.description,
            frequency=recurring_transaction.frequency,
            start_date=recurring_transaction.start_date,
            next_due_date=recurring_transaction.next_due_date,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()

@router.get("/recurring-transactions/", response_model=List[RecurringTransactionInDB])
async def read_recurring_transactions(
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, amount, type, category, description, frequency, start_date, next_due_date FROM recurring_transactions WHERE user_id = ?",
        (current_user.id,),
    )
    recurring_transactions_data = cursor.fetchall()
    conn.close()
    return [RecurringTransactionInDB(**rt) for rt in recurring_transactions_data]

@router.put("/recurring-transactions/{recurring_transaction_id}", response_model=RecurringTransactionInDB)
async def update_recurring_transaction(
    recurring_transaction_id: str,
    recurring_transaction: RecurringTransactionCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE recurring_transactions SET name = ?, amount = ?, type = ?, category = ?, description = ?, frequency = ?, start_date = ?, next_due_date = ? WHERE id = ? AND user_id = ?",
        (
            recurring_transaction.name,
            recurring_transaction.amount,
            recurring_transaction.type,
            recurring_transaction.category,
            recurring_transaction.description,
            recurring_transaction.frequency,
            recurring_transaction.start_date.isoformat(),
            recurring_transaction.next_due_date.isoformat(),
            recurring_transaction_id,
            current_user.id,
        ),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")
    conn.close()
    return RecurringTransactionInDB(
        id=recurring_transaction_id,
        user_id=current_user.id,
        name=recurring_transaction.name,
        amount=recurring_transaction.amount,
        type=recurring_transaction.type,
        category=recurring_transaction.category,
        description=recurring_transaction.description,
        frequency=recurring_transaction.frequency,
        start_date=recurring_transaction.start_date,
        next_due_date=recurring_transaction.next_due_date,
    )

@router.delete("/recurring-transactions/{recurring_transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_transaction(
    recurring_transaction_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM recurring_transactions WHERE id = ? AND user_id = ?",
        (recurring_transaction_id, current_user.id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")
    conn.close()
    return