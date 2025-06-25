from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from app.models.models import CategoryCreate, CategoryInDB, UserInDB
from app.auth.auth import get_current_active_user
from app.data.database import get_db_connection

router = APIRouter()

@router.post("/categories/", response_model=CategoryInDB)
async def create_category(
    category: CategoryCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    category_id = str(uuid.uuid4())
    try:
        cursor.execute(
            "INSERT INTO categories (id, user_id, name, type) VALUES (?, ?, ?, ?)",
            (category_id, current_user.id, category.name, category.type),
        )
        conn.commit()
        return CategoryInDB(
            id=category_id,
            user_id=current_user.id,
            name=category.name,
            type=category.type,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()

@router.get("/categories/", response_model=List[CategoryInDB])
async def read_categories(
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, type FROM categories WHERE user_id = ?",
        (current_user.id,),
    )
    categories_data = cursor.fetchall()
    conn.close()
    return [CategoryInDB(**c) for c in categories_data]

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM categories WHERE id = ? AND user_id = ?",
        (category_id, current_user.id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    conn.close()
    return