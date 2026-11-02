from collections.abc import Mapping
from typing import Any, Protocol


class RawResponseProtocol(Protocol):
    @property
    def headers(self):
        return Mapping[str, str]

    @property
    def text(self):
        return self.text

    @property
    def status_code(self) -> int:
        return self.status_code

    def json(self) -> Any: ...
