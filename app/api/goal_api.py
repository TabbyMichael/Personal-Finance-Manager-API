from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from app.models.models import GoalCreate, GoalInDB, UserInDB
from app.auth.auth import get_current_active_user
from app.data.database import get_db_connection

router = APIRouter()

@router.post("/goals/", response_model=GoalInDB)
async def create_goal(
    goal: GoalCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    goal_id = str(uuid.uuid4())
    try:
        cursor.execute(
            "INSERT INTO goals (id, user_id, name, target_amount, current_amount, target_date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                goal_id,
                current_user.id,
                goal.name,
                goal.target_amount,
                goal.current_amount,
                goal.target_date.isoformat(),
            ),
        )
        conn.commit()
        return GoalInDB(
            id=goal_id,
            user_id=current_user.id,
            name=goal.name,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            target_date=goal.target_date,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()

@router.get("/goals/", response_model=List[GoalInDB])
async def read_goals(
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, target_amount, current_amount, target_date FROM goals WHERE user_id = ?",
        (current_user.id,),
    )
    goals_data = cursor.fetchall()
    conn.close()
    return [GoalInDB(**g) for g in goals_data]

@router.put("/goals/{goal_id}", response_model=GoalInDB)
async def update_goal(
    goal_id: str,
    goal: GoalCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET name = ?, target_amount = ?, current_amount = ?, target_date = ? WHERE id = ? AND user_id = ?",
        (
            goal.name,
            goal.target_amount,
            goal.current_amount,
            goal.target_date.isoformat(),
            goal_id,
            current_user.id,
        ),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    conn.close()
    return GoalInDB(
        id=goal_id,
        user_id=current_user.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
    )

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM goals WHERE id = ? AND user_id = ?",
        (goal_id, current_user.id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    conn.close()
    return