class AccountNotFound(Exception):
    """Raised when no account exists for an ID."""

    def __init__(self, account_id: str):
        super().__init__(f"account {account_id} does not exist")


class InsufficientFunds(Exception):
    """The account has insufficient funds."""

    def __init__(self, *, current_balance: int, attempted_amount: int):
        super().__init__(
            f"tried to withdraw {attempted_amount} when only {current_balance} is available"
        )
