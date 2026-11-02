from typing import Any

from spud import raw_response_protocol, response_checks


class ApiResponse:
    def __init__(self, raw_response: raw_response_protocol.RawResponseProtocol) -> None:
        self.raw = raw_response
        self._checker = None

    def json(self) -> Any:
        return self.raw.json()

    @property
    def status_code(self):
        return self.raw.status_code

    @property
    def headers(self):
        return self.raw.headers

    @property
    def text(self):
        return self.raw.text

    @property
    def check(self):
        if self._checker is None:
            checker = response_checks.ResponseChecks(response=self)
            self._checker = checker
        return self._checker
