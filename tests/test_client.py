import io
import json
from urllib.error import HTTPError

import pytest

from lumi_aitta_api import AittaClient, AittaError, Settings
from lumi_aitta_api import client as module
from lumi_aitta_api.cli import main


@pytest.fixture
def transport(monkeypatch):
    calls, responses = [], {}
    monkeypatch.setenv("AITTA_API_KEY", "project-secret")

    class Opener:
        def open(self, request, timeout):
            calls.append((request.full_url, request.method, request.headers, timeout))
            result = responses[request.full_url.removeprefix(module.API_URL)]
            if isinstance(result, Exception):
                raise result
            return io.BytesIO(result if isinstance(result, bytes) else json.dumps(result).encode())

    monkeypatch.setattr(module, "build_opener", lambda *args: Opener())
    return AittaClient(Settings.from_env()), responses, calls


def details():
    return {"id": "vendor/model", "capabilities": ["openai-chat-completion"],
            "_links": {"preload": {"href": "/model/vendor~model/preload", "method": "POST"}}}


def test_discovery_never_loads_models_or_follows_links(transport):
    client, responses, calls = transport
    responses["/model"] = {"_links": {"item": [{"name": "vendor/model", "href": "https://evil.invalid"}]}}
    responses["/model/vendor~model"] = details()
    responses["/status"] = {"is_available": True, "reason": "backend private details"}
    responses["/worker/vendor~model"] = {"_embedded": {"workers": [{"model": "vendor/model", "status": "requested"}]}}
    assert client.models()["models"] == ["vendor/model"]
    assert client.model("vendor/model")["capabilities"] == ["openai-chat-completion"]
    assert client.status()["is_available"]
    assert client.workers("vendor/model")["workers"] == [{"status": "requested"}]
    assert all(call[1] == "GET" for call in calls)
    assert all(call[0].startswith(module.API_URL + "/") for call in calls)
    assert "backend private details" not in json.dumps(client.status())


@pytest.mark.parametrize("response", [{}, b""])
def test_preload_requests_exact_post_and_reports_unverified(transport, response):
    client, responses, calls = transport
    responses["/model/vendor~model"] = details()
    responses["/model/vendor~model/preload"] = response
    assert client.preload("vendor/model")["state"] == "preload_requested"
    assert [call[1] for call in calls] == ["GET", "POST"]
    assert calls[-1][2]["Authorization"] == "Bearer project-secret"


@pytest.mark.parametrize("href", ["https://evil.invalid/preload", "//evil.invalid/preload", "/wrong/preload"])
def test_untrusted_preload_links_never_receive_credentials(transport, href):
    client, responses, calls = transport
    data = details()
    data["_links"]["preload"]["href"] = href
    responses["/model/vendor~model"] = data
    with pytest.raises(AittaError, match="expected preload"):
        client.preload("vendor/model")
    assert len(calls) == 1


@pytest.mark.parametrize("status", [302, 401, 429, 500])
def test_http_error_is_sanitized_and_not_retried(transport, status, capsys):
    _, responses, calls = transport
    responses["/model"] = HTTPError(module.API_URL, status, "project-secret", {}, io.BytesIO(b"private details"))
    assert main(["models"]) == 1
    output = capsys.readouterr().err
    assert str(status) in output
    assert "project-secret" not in output and "private details" not in output
    assert len(calls) == 1


@pytest.mark.parametrize("route,response,operation", [
    ("/model", {}, lambda c: c.models()),
    ("/model", {"_links": {"item": [None]}}, lambda c: c.models()),
    ("/model", b"x" * 1_000_001, lambda c: c.models()),
    ("/status", {"is_available": "yes"}, lambda c: c.status()),
    ("/worker/vendor~model", {}, lambda c: c.workers("vendor/model")),
    ("/model/vendor~model", {"id": "different", "capabilities": []}, lambda c: c.model("vendor/model")),
], ids=["missing-model-links", "invalid-model-item", "oversized-response", "invalid-status", "missing-workers", "wrong-model"])
def test_malformed_responses_fail_closed(transport, route, response, operation):
    client, responses, _ = transport
    responses[route] = response
    with pytest.raises(AittaError):
        operation(client)


def test_settings_hide_secrets_and_do_not_fall_back(monkeypatch):
    assert "project-secret" not in repr(Settings("project-secret"))
    monkeypatch.delenv("AITTA_API_KEY", raising=False)
    monkeypatch.setenv("VLLM_API_KEY", "other-token")
    with pytest.raises(ValueError, match="AITTA_API_KEY"):
        Settings.from_env()


def test_no_redirect_handler_rejects_forwarding():
    assert module.NoRedirects().redirect_request(None, None, 302, "", {}, "https://evil.invalid") is None
