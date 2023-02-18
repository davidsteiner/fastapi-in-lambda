from typing import Generator

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb
from vivaldi.app import app

_TABLE_NAME = "TestTable"


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    monkeypatch.setenv("TABLE_NAME", _TABLE_NAME)


@pytest.fixture(scope="session", autouse=True)
def dynamodb_table():
    with mock_dynamodb():
        client = boto3.client("dynamodb", region_name="eu-west-1")
        client.create_table(
            TableName=_TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield client


@pytest.fixture(scope="session")
def app_client() -> Generator[TestClient, None, None]:
    """Get a test client."""
    with TestClient(app) as c:
        yield c
