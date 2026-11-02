from typing import Any
from unittest.mock import Mock

import httpx

from spud import httpx_transport


class FakeResponse:
    def __init__(self):
        self.headers = {}

    status_code = 200
    text = "text"

    def json(self) -> Any:
        return {"status": "ok"}


def test_request_httpx(monkeypatch):
    url = "http://google.com/"
    headers = {"Authorization": "Bearer Token..."}
    params = {"q": 123}
    json = {"status": "ok"}
    request_httpx_mock = Mock()
    fake_response = FakeResponse()
    request_httpx_mock.return_value = fake_response
    monkeypatch.setattr(httpx, "request", request_httpx_mock)
    transport = httpx_transport.HttpxTransport()
    response = transport.request(
        method="POST", url=url, headers=headers, params=params, json=json
    )
    request_httpx_mock.assert_called_once_with(
        method="POST", url=url, headers=headers, params=params, json=json
    )
    assert response is fake_response
