from fastapi import FastAPI
from app.api import user_api, transaction_api, category_api, recurring_transaction_api, goal_api, report_api
from app.data.database import create_tables

app = FastAPI(
    title="Personal Finance Manager API",
    description="API for managing personal finances locally.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(user_api.router, prefix="/users", tags=["users"])
app.include_router(transaction_api.router, prefix="/transactions", tags=["transactions"])
app.include_router(category_api.router, prefix="/categories", tags=["categories"])
app.include_router(recurring_transaction_api.router, prefix="/recurring-transactions", tags=["recurring-transactions"])
app.include_router(goal_api.router, prefix="/goals", tags=["goals"])
app.include_router(report_api.router, prefix="/reports", tags=["reports"])

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the Personal Finance Manager API"}