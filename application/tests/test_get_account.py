from fastapi.testclient import TestClient


def test_get_existing_account(app_client: TestClient):
    response = app_client.post("/account")

    assert response.status_code == 200
    account_id = response.json()["account_id"]

    response = app_client.get(f"/account/{account_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 0


def test_get_nonexistent_account_raises_404(app_client: TestClient):
    response = app_client.get("/account/missing_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "account not found"
