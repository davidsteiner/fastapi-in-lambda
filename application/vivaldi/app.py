from typing import Literal

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI(
    title="Vivaldi API",
    description="HTTP API for Vivaldi Bank",
    version="1.0",
)


class Transaction(BaseModel):
    """A bank transaction."""

    action: Literal["deposit", "withdraw"]
    amount: int


class Balance(BaseModel):
    """The balance of a user."""

    user_id: str
    balance: int


class Transactions(Balance):
    """The transactions and overall balance of a user."""

    transactions: list[Transaction]


@app.put("/user/{user_id}/transactions")
def put_transaction(user_id: str, transaction: Transaction) -> Balance:
    """Put a new transaction."""
    return Balance(user_id=user_id, balance=100)


@app.get("/user/{user_id}/transactions")
def get_transactions(user_id: str) -> Transactions:
    """Get all transactions and the overall balance."""
    return Transactions(user_id=user_id, balance=100, transactions=[])


handler = Mangum(app, lifespan="off")
