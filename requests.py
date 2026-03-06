"""Минимальный совместимый слой requests для окружений без внешнего пакета.

Поддерживает requests.get/post(..., timeout=...) и RequestException.
"""
from __future__ import annotations

import urllib.request
import urllib.error


class RequestException(Exception):
    pass


class Response:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def _do_request(req: urllib.request.Request, timeout: int = 5) -> Response:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return Response(text=body, status_code=getattr(resp, 'status', 200))
    except (urllib.error.URLError, ValueError) as exc:
        raise RequestException(str(exc))


def get(url: str, timeout: int = 5) -> Response:
    req = urllib.request.Request(url=url, method='GET')
    return _do_request(req, timeout=timeout)


def post(url: str, data=None, timeout: int = 5) -> Response:
    raw = b'' if data is None else str(data).encode('utf-8')
    req = urllib.request.Request(url=url, data=raw, method='POST')
    return _do_request(req, timeout=timeout)
