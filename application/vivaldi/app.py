import uuid

from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic.main import BaseModel
from vivaldi.persistence import (
    AccountRecord,
    Transaction,
    load_account,
    open_account,
    store_transaction,
)

app = FastAPI(
    title="Vivaldi API",
    description="HTTP API for Vivaldi Bank",
    version="1.0",
)


class Account(BaseModel):
    account_id: str
    balance: int

    @staticmethod
    def from_record(account_record: AccountRecord):
        return Account(
            account_id=account_record.account_id, balance=account_record.amount
        )


@app.post("/account/{account_id}/transactions")
def post_transaction(account_id: str, transaction: Transaction) -> Account:
    """Put a new transaction."""
    return Account.from_record(store_transaction(account_id, transaction))


@app.post("/account")
def post_account() -> Account:
    """Open a new account."""
    account_id = uuid.uuid4().hex
    return Account.from_record(open_account(account_id))


@app.get("/account/{account_id}")
def get_account(account_id) -> Account:
    """Get the details of an account."""
    record = load_account(account_id)

    if record:
        return Account.from_record()
    else:
        raise HTTPException(status_code=404, detail="account not found")


handler = Mangum(app, lifespan="off")
