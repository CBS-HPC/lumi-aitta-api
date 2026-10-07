from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .settings import Settings

API_URL = "https://aitta-api.csc.fi"
OPENAI_URL = API_URL + "/openai/v1"


class AittaError(RuntimeError):
    """Sanitized API failure; upstream credentialed bodies are never exposed."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def model_route(model: str) -> str:
    if not isinstance(model, str) or not model or len(model) > 256 or any(ord(c) < 32 for c in model):
        raise ValueError("Invalid AITTA model ID")
    return "/model/" + quote(model.replace("/", "~"), safe="")


class AittaClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._opener = build_opener(NoRedirects())

    def _request(self, route: str, *, method: str = "GET") -> dict:
        request = Request(API_URL + route, method=method, headers={
            "Authorization": "Bearer " + self.settings.api_key, "Accept": "application/json"})
        try:
            with self._opener.open(request, timeout=30) as response:
                raw = response.read(1_000_001)
            if not raw and method == "POST":
                return {}
            if len(raw) > 1_000_000:
                raise ValueError("Oversized response")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Invalid response")
            return data
        except HTTPError as exc:
            code = exc.code
            exc.close()
            raise AittaError(f"AITTA HTTP {code}; response body withheld; no automatic retry") from None
        except (URLError, OSError):
            raise AittaError("AITTA transport failure; no automatic retry") from None
        except (ValueError, UnicodeError):
            raise AittaError("AITTA invalid or oversized response") from None

    def models(self) -> dict:
        data = self._request("/model")
        links = data.get("_links")
        if not isinstance(links, dict) or "item" not in links:
            raise AittaError("AITTA invalid model listing")
        items = links["item"]
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list) or any(not isinstance(item, dict) or
                                             not isinstance(item.get("name"), str) for item in items):
            raise AittaError("AITTA invalid model listing")
        return {"platform": "lumi-aitta", "models": [item["name"] for item in items]}

    def _model_details(self, model: str) -> dict:
        details = self._request(model_route(model))
        if details.get("id") != model or not isinstance(details.get("capabilities"), list) or any(
                not isinstance(value, str) for value in details["capabilities"]):
            raise AittaError("AITTA invalid model details")
        return details

    def model(self, model: str) -> dict:
        details = self._model_details(model)
        return {"platform": "lumi-aitta", "model": model, "capabilities": details["capabilities"]}

    def status(self) -> dict:
        data = self._request("/status")
        retry = data.get("retry_after_seconds")
        if not isinstance(data.get("is_available"), bool) or (retry is not None and
                (isinstance(retry, bool) or not isinstance(retry, int) or retry < 0)):
            raise AittaError("AITTA invalid service status")
        return {"platform": "lumi-aitta", "is_available": data["is_available"],
                "retry_after_seconds": retry}

    def workers(self, model: str) -> dict:
        data = self._request(model_route(model).replace("/model/", "/worker/", 1))
        embedded = data.get("_embedded")
        if not isinstance(embedded, dict) or not isinstance(embedded.get("workers"), list):
            raise AittaError("AITTA invalid worker listing")
        items = embedded["workers"]
        if any(not isinstance(item, dict) or item.get("model") != model or
               not isinstance(item.get("status"), str) for item in items):
            raise AittaError("AITTA invalid worker listing")
        return {"platform": "lumi-aitta", "model": model,
                "workers": [{"status": item["status"]} for item in items]}

    def preload(self, model: str) -> dict:
        route = model_route(model)
        details = self._model_details(model)
        links = details.get("_links")
        link = links.get("preload") if isinstance(links, dict) else None
        if not isinstance(link, dict) or link.get("method") != "POST" or link.get("href") != route + "/preload":
            raise AittaError("AITTA model does not advertise the expected preload operation")
        # Never forward the project token to a URL supplied by an API response.
        self._request(route + "/preload", method="POST")
        return {"platform": "lumi-aitta", "model": model, "state": "preload_requested",
                "note": "Loading requested; use workers and inference to establish readiness."}
