from collections.abc import Mapping
from typing import Any

from . import api_response, httpx_transport, transport_protocol
from .transport_protocol import HttpMethod


class ApiClient:
    def __init__(
        self,
        base_url: str,
        transport: transport_protocol.TransportProtocol | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        if transport is None:
            self.transport: transport_protocol.TransportProtocol = (
                httpx_transport.HttpxTransport()
            )
        else:
            self.transport = transport
        self.headers = headers

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> api_response.ApiResponse:
        return self.request(method="GET", path=path, params=params, headers=headers)

    def post(
        self, path: str, json: Any = None, headers: Mapping[str, str] | None = None
    ) -> api_response.ApiResponse:
        return self.request(method="POST", path=path, json=json, headers=headers)

    def put(
        self, path: str, json: Any = None, headers: Mapping[str, str] | None = None
    ) -> api_response.ApiResponse:
        return self.request(method="PUT", path=path, json=json, headers=headers)

    def patch(
        self, path: str, json: Any = None, headers: Mapping[str, str] | None = None
    ) -> api_response.ApiResponse:
        return self.request(method="PATCH", path=path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> api_response.ApiResponse:
        return self.request(method="DELETE", path=path, headers=headers, params=params)

    def request(
        self,
        method: HttpMethod,
        path: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any = None,
    ) -> api_response.ApiResponse:
        if not path.startswith("/"):
            raise ValueError("Path should start with '/'")
        if headers is None:
            effective_headers = self.headers
        else:
            if self.headers is None:
                effective_headers = headers
            else:
                update_headers = dict(self.headers)
                update_headers.update(headers)
                effective_headers = update_headers

        raw_response = self.transport.request(
            method=method,
            url=self.base_url + path,
            params=params,
            headers=effective_headers,
            json=json,
        )
        return api_response.ApiResponse(raw_response)
