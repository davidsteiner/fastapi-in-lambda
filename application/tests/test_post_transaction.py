from fastapi.testclient import TestClient


def test_deposit(app_client: TestClient) -> None:
    response = app_client.post("/account")

    assert response.status_code == 200
    account_id = response.json()["account_id"]

    # Now we deposit a 100
    payload = {
        "action": "deposit",
        "amount": 100,
    }
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 200
    assert response.json()["balance"] == 100

    # And another 100
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 200
    assert response.json()["balance"] == 200


def test_withdraw(app_client: TestClient) -> None:
    response = app_client.post("/account")

    assert response.status_code == 200
    account_id = response.json()["account_id"]

    # Now we deposit a 100
    payload = {
        "action": "deposit",
        "amount": 100,
    }
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 200
    assert response.json()["balance"] == 100

    # And withdraw half of it
    payload = {
        "action": "withdraw",
        "amount": 50,
    }
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 200
    assert response.json()["balance"] == 50


def test_withdrawing_too_much_fails(app_client: TestClient) -> None:
    response = app_client.post("/account")

    assert response.status_code == 200
    account_id = response.json()["account_id"]

    # Now we deposit a 100
    payload = {
        "action": "deposit",
        "amount": 100,
    }
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 200
    assert response.json()["balance"] == 100

    # And try to withdraw more than 100, which should be forbidden
    payload = {
        "action": "withdraw",
        "amount": 150,
    }
    response = app_client.post(f"/account/{account_id}/transactions", json=payload)
    assert response.status_code == 403
    assert (
        response.json()["reason"] == "tried to withdraw 150 when only 100 is available"
    )


def test_transaction_for_missing_account_responds_with_404(
    app_client: TestClient,
) -> None:
    payload = {
        "action": "deposit",
        "amount": 100,
    }
    response = app_client.post("/account/missing_id/transactions", json=payload)
    assert response.status_code == 404
    assert response.json()["reason"] == "account missing_id does not exist"
