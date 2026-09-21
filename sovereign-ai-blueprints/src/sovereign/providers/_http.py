"""Minimal JSON-over-HTTP helper (stdlib only, so the repo installs with no deps)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class ProviderError(RuntimeError):
    pass


def post_json(url: str, payload: dict, headers: dict[str, str], timeout: float = 60.0) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("content-type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        raise ProviderError(f"{exc.code} from {url}: {exc.read().decode('utf-8', 'replace')[:400]}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise ProviderError(f"could not reach {url}: {exc.reason}") from exc
