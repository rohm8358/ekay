import os

from ekay.server import create_app


def test_hexstrike_style_no_token():
    os.environ.pop("EKAY_TOKEN", None)
    client = create_app().test_client()
    h = client.get("/health")
    assert h.status_code == 200
    assert h.get_json()["auth_required"] is False
    tools = client.get("/api/tools")
    assert tools.status_code == 200
    assert tools.get_json()["count"] > 0


def test_optional_token_when_set(monkeypatch):
    monkeypatch.setenv("EKAY_TOKEN", "secret")
    client = create_app().test_client()
    assert client.get("/api/tools").status_code == 401
    ok = client.get("/api/tools", headers={"Authorization": "Bearer secret"})
    assert ok.status_code == 200
