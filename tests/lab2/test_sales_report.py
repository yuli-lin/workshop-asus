import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.lab2


def test_normal_request_returns_category_items_and_total(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert isinstance(body["items"], list)
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Zenbook 14 OLED"
    assert body["total"] == 42900


def test_normal_request_with_explicit_formula(client: TestClient) -> None:
    response = client.get(
        "/reports/sales", params={"category": "Gaming Laptop", "formula": "total"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Gaming Laptop"
    assert body["total"] == 62900


def test_empty_category_returns_no_items(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Nonexistent"})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Nonexistent"
    assert body["items"] == []
    assert body["total"] == 0


# ---- SQL injection regression -------------------------------------------------


def test_sql_injection_in_category_does_not_return_extra_rows(
    client: TestClient,
) -> None:
    # A classic SQL injection payload that would return all rows with string interpolation.
    response = client.get(
        "/reports/sales", params={"category": "' OR '1'='1"}
    )

    assert response.status_code == 200
    body = response.json()
    # Parameterized query treats the payload as a literal string; no rows match.
    assert body["items"] == []
    assert body["total"] == 0


def test_sql_injection_union_does_not_leak_data(client: TestClient) -> None:
    payload = "Laptop' UNION SELECT 1,'leaked','secret',9999--"
    response = client.get("/reports/sales", params={"category": payload})

    assert response.status_code == 200
    body = response.json()
    # Parameterized query prevents UNION injection; no extra rows returned.
    assert body["items"] == []
    assert body["total"] == 0


# ---- Code injection regression ------------------------------------------------


def test_formula_code_injection_is_rejected(client: TestClient) -> None:
    # An eval()-based implementation would execute this; it must be rejected.
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').getcwd()"},
    )

    assert response.status_code == 422


def test_formula_arbitrary_expression_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total * 2"},
    )

    assert response.status_code == 422


# ---- Error disclosure regression ----------------------------------------------


def test_error_response_does_not_contain_traceback(client: TestClient) -> None:
    # An injection attempt that would previously trigger an exception and return
    # a raw traceback in the response body.
    response = client.get(
        "/reports/sales",
        params={"category": "' OR '1'='1"},
    )

    body = response.text
    assert "Traceback" not in body
    assert "traceback" not in body
    assert "sqlite3" not in body
    assert "File " not in body


def test_formula_error_response_does_not_disclose_internals(
    client: TestClient,
) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "open('/etc/passwd').read()"},
    )

    assert response.status_code == 422
    body = response.text
    assert "Traceback" not in body
    assert "eval" not in body
