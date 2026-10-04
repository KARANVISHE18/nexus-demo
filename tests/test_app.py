import pytest

from app import add, app, divide


def test_add():
    assert add(2, 3) == 5


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_health_endpoint():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_add_route():
    client = app.test_client()
    assert client.get("/add/4/6").get_json() == {"result": 10}
