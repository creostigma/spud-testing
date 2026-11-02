from collections.abc import Mapping
from typing import Any

import httpx

from . import raw_response_protocol
from .transport_protocol import HttpMethod


class HttpxTransport:
    def request(
        self,
        method: HttpMethod,
        url: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any = None,
    ) -> raw_response_protocol.RawResponseProtocol:
        return httpx.request(
            method=method, url=url, params=params, headers=headers, json=json
        )
