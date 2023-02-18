import os
from functools import lru_cache
from typing import Literal, Optional

import boto3
from pydantic import BaseModel, Field

_ACCOUNT_SK = "summary"


class Transaction(BaseModel):
    """A bank transaction."""

    action: Literal["deposit", "withdraw"]
    amount: int


class AccountRecord(BaseModel):
    """The overall balance."""

    account_id: str = Field(alias="pk")
    amount: int
    transaction_counter: int

    def apply_transaction(self, transaction: Transaction):
        """Apply a transaction to this balance."""
        updated_amount = (
            self.amount + transaction.amount
            if transaction.action == "deposit"
            else self.amount - transaction.amount
        )
        return self.copy(
            update={
                "transaction_counter": self.transaction_counter + 1,
                "amount": updated_amount,
            }
        )


def open_account(account_id: str) -> AccountRecord:
    table = dynamodb_table()
    account = AccountRecord(
        pk=account_id,
        amount=0,
        transaction_counter=0,
    )
    table.put_item(Item={"sk": _ACCOUNT_SK, **account.dict(by_alias=True)})

    return account


def load_account(account_id: str) -> Optional[AccountRecord]:
    """Get the account for the supplied account ID."""
    table = dynamodb_table()
    response = table.get_item(Key={"pk": account_id, "sk": _ACCOUNT_SK})

    if item := response.get("Item"):
        return AccountRecord.parse_obj(item)
    else:
        return None


def store_transaction(account_id: str, transaction: Transaction) -> AccountRecord:
    """Get the summary for a user."""
    previous_balance = load_account(account_id)

    if not previous_balance:
        raise AccountNotFound(f"no account found for {account_id}")
    if (
        transaction.action == "withdraw"
        and previous_balance.amount < transaction.amount
    ):
        raise InsufficientFunds(f"account only has {previous_balance.amount}")

    new_balance = previous_balance.apply_transaction(transaction)
    _persist_transaction_and_balance(new_balance, transaction)

    return new_balance


def _persist_transaction_and_balance(account: AccountRecord, transaction: Transaction):
    client = _create_client()

    items = [
        {
            "Put": {
                "TableName": _table_name(),
                "Item": {
                    "pk": {"S": account.account_id},
                    "sk": {"S": _ACCOUNT_SK},
                    "amount": {"N": str(account.amount)},
                    "transaction_counter": {"N": str(account.transaction_counter)},
                },
            }
        },
        {
            "Put": {
                "TableName": _table_name(),
                "Item": {
                    "pk": {"S": account.account_id},
                    "sk": {"S": f"TRANS#{account.transaction_counter}"},
                    "amount": {"N": str(transaction.amount)},
                    "action": {"S": transaction.action},
                },
                "ConditionExpression": "attribute_not_exists(sk)",
            }
        },
    ]

    client.transact_write_items(TransactItems=items)


@lru_cache(maxsize=1)
def dynamodb_table():
    resource = boto3.resource(
        "dynamodb", endpoint_url=os.getenv("DYNAMODB_ENDPOINT_OVERRIDE")
    )
    return resource.Table(_table_name())


@lru_cache(maxsize=1)
def _create_client():
    return boto3.client(
        "dynamodb", endpoint_url=os.getenv("DYNAMODB_ENDPOINT_OVERRIDE")
    )


def _table_name() -> str:
    return os.environ["TABLE_NAME"]


class AccountNotFound(Exception):
    """Raised when no account exists for an ID."""


class InsufficientFunds(Exception):
    """The account has insufficient funds."""
