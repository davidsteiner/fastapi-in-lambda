import uuid

from fastapi import FastAPI
from mangum import Mangum
from vivaldi.persistence import Account, Transaction, open_account, store_transaction

app = FastAPI(
    title="Vivaldi API",
    description="HTTP API for Vivaldi Bank",
    version="1.0",
)


@app.post("/account/{account_id}/transactions")
def post_transaction(account_id: str, transaction: Transaction) -> Account:
    """Put a new transaction."""
    return store_transaction(account_id, transaction)


@app.post("/account")
def post_account() -> Account:
    """Open a new account."""
    account_id = uuid.uuid4().hex
    return open_account(account_id)


handler = Mangum(app, lifespan="off")
