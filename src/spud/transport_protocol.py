from collections.abc import Mapping
from typing import Any, Literal, Protocol

from spud import raw_response_protocol

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class TransportProtocol(Protocol):
    def request(
        self,
        method: HttpMethod,
        url: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any = None,
    ) -> raw_response_protocol.RawResponseProtocol: ...
