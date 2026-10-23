from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import assessments, supabase_auth


def test_supabase_clients_use_http1(monkeypatch):
    captured = []
    real_client = httpx.Client

    def capture(**kwargs):
        captured.append(kwargs)
        return real_client(**kwargs)

    monkeypatch.setattr(supabase_auth.httpx, "Client", capture)
    options = supabase_auth.client_options()
    try:
        assert captured[0]["http2"] is False
        assert options.httpx_client.timeout.connect == 10
    finally:
        options.httpx_client.close()


def test_database_socket_failure_returns_readable_503(client, monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ReadError("Windows socket failure")

    monkeypatch.setattr(assessments, "answer_rows", fail)
    response = client.get("/api/student/results")
    assert response.status_code == 503
    assert "temporarily unreachable" in response.json()["detail"]
    assert "Windows socket" not in response.text


def test_auth_network_failure_does_not_report_invalid_login(monkeypatch):
    def fail(*args):
        raise httpx.ConnectError("Offline")

    monkeypatch.setattr(supabase_auth, "public_client", lambda: SimpleNamespace(auth=SimpleNamespace(get_user=fail)))
    with pytest.raises(HTTPException) as error:
        supabase_auth.current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token"))
    assert error.value.status_code == 503
