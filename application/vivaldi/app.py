import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic.main import BaseModel
from vivaldi.exceptions import AccountNotFound, InsufficientFunds
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
    def from_record(account_record: AccountRecord) -> "Account":
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
def get_account(account_id: str) -> Account:
    """Get the details of an account."""
    record = load_account(account_id)

    if record:
        return Account.from_record(record)
    else:
        raise HTTPException(status_code=404, detail="account not found")


@app.exception_handler(InsufficientFunds)
def handle_insufficient_funds(
    _request: Request, exc: InsufficientFunds
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"reason": str(exc)})


@app.exception_handler(AccountNotFound)
def handle_account_not_found(_request: Request, exc: InsufficientFunds) -> JSONResponse:
    return JSONResponse(status_code=404, content={"reason": str(exc)})


handler = Mangum(app, lifespan="off")
