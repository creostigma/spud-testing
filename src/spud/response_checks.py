from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from spud.exceptions import SpudCheckError

_MISSING = object()


class ResponseChecks:
    if TYPE_CHECKING:
        from . import api_response

    def __init__(self, response: "api_response.ApiResponse") -> None:
        self.response = response

    def status(self, expected_status: int) -> "ResponseChecks":
        status = self.response.status_code
        phrase = f"Expected status {expected_status}, got {status}"
        if status != expected_status:
            try:
                phrase = phrase + f" {HTTPStatus(status).phrase}"
            except ValueError:
                pass

            raise SpudCheckError(phrase)
        return self

    def json_path(self, path: str = "", expected: Any = _MISSING) -> "ResponseChecks":
        if expected is _MISSING:
            raise TypeError("json_path() missing required argument: expected")
        current = self.response.json()
        for key in parse_json_path(path=path):
            if not (
                (isinstance(current, dict) and isinstance(key, str))
                or (isinstance(current, list) and isinstance(key, int))
            ):
                raise SpudCheckError(f"JSON path {path!r} not found")

            try:
                if isinstance(current, dict) and isinstance(key, str):
                    current = current[key]
                elif isinstance(current, list) and isinstance(key, int):
                    current = current[key]
            except (KeyError, IndexError):
                raise SpudCheckError(f"JSON path {path!r} not found") from None
        if not self.json_equal(current, expected):
            raise SpudCheckError(f"expected {expected!r}, got {current!r}")
        return self

    def json_equal(self, actual: Any, expected: Any) -> bool:
        if type(actual) != type(expected):
            return False
        if isinstance(actual, dict):
            if actual.keys() != expected.keys():
                return False
            for key in actual:
                if not self.json_equal(actual[key], expected[key]):
                    return False
            return True
        if isinstance(actual, list):
            if len(actual) != len(expected):
                return False
            for actual_item, expected_item in zip(actual, expected):
                if not self.json_equal(actual_item, expected_item):
                    return False
            return True
        return actual == expected


def parse_json_path(path: str) -> list[str | int]:
    tokens: list[str | int] = []
    buffer = ""
    inside_brackets = False
    after_closing_bracket = False
    if path.endswith("."):
        raise ValueError(f"Invalid JSON path {path!r}: empty path segment")
    for index, char in enumerate(path):
        if char == "[":
            if inside_brackets:
                raise ValueError(
                    f"Invalid JSON path {path!r}: unexpected opening bracket"
                )
            if index > 0 and path[index - 1] == ".":
                raise ValueError(
                    f"Invalid JSON path {path!r}: unexpected opening bracket"
                )
            if buffer:
                tokens.append(buffer)
                buffer = ""
            inside_brackets = True
            after_closing_bracket = False
            continue
        if char == "]":
            if not inside_brackets:
                raise ValueError(
                    f"Invalid JSON path {path!r}: unexpected closing bracket"
                )
            if buffer:
                try:
                    tokens.append(int(buffer))
                except ValueError:
                    raise ValueError(
                        f"Invalid JSON path {path!r}: array index must be an integer"
                    ) from None
            else:
                raise ValueError(
                    f"Invalid JSON path {path!r}: array index cannot be empty"
                ) from None
            buffer = ""
            inside_brackets = False
            after_closing_bracket = True
            continue
        if char == ".":
            if inside_brackets:
                raise ValueError(
                    f"Invalid JSON path {path!r}: array index must be integer"
                )
            if buffer == "" and not after_closing_bracket:
                raise ValueError(f"Invalid JSON path {path!r}: empty path segment")
            if buffer:
                tokens.append(buffer)
                buffer = ""
            after_closing_bracket = False
            continue
        if after_closing_bracket:
            raise ValueError(
                f"Invalid JSON path {path!r}: expected separator after closing bracket"
            )
        buffer += char
    if buffer:
        tokens.append(buffer)
    if inside_brackets:
        raise ValueError(f"Invalid JSON path {path!r}: unclosed bracket")
    return tokens
