from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TransactionBase(BaseModel):
    date: date
    amount: float = Field(..., gt=0)
    type: str # "income" or "expense"
    category: str
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    id: str
    user_id: str

class CategoryBase(BaseModel):
    name: str
    type: str # "income" or "expense"

class CategoryCreate(CategoryBase):
    pass

class CategoryInDB(CategoryBase):
    id: str
    user_id: str

class RecurringTransactionBase(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    type: str # "income" or "expense"
    category: str
    description: Optional[str] = None
    frequency: str # e.g., "daily", "weekly", "monthly", "yearly"
    start_date: date
    next_due_date: date

class RecurringTransactionCreate(RecurringTransactionBase):
    pass

class RecurringTransactionInDB(RecurringTransactionBase):
    id: str
    user_id: str

class GoalBase(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(0, ge=0)
    target_date: date

class GoalCreate(GoalBase):
    pass

class GoalInDB(GoalBase):
    id: str
    user_id: str

class ReportSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    spending_by_category: dict[str, float]
    income_by_category: dict[str, float]