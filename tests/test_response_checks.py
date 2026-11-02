from unittest.mock import Mock

import pytest

from spud import api_response, exceptions, raw_response_protocol
from spud.response_checks import parse_json_path


def test_check_status_passes_when_status_matches():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.status_code = 200

    response = api_response.ApiResponse(raw_response_mock)

    response.check.status(200)


def test_check_status_error_when_status_not_matches():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.status_code = 500

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        exceptions.SpudCheckError,
        match=r"^Expected status 200, got 500 Internal Server Error",
    ):
        response.check.status(200)


def test_check_got_uncommon_status():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.status_code = 599

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        exceptions.SpudCheckError, match=r"^Expected status 200, got 599$"
    ):
        response.check.status(200)


def test_json_path_checks_nested_field():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"customer": {"name": "Alex"}}

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path("customer.name", "Alex")


def test_json_path_not_have_field():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"customer": {"name": "Alex"}}

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        exceptions.SpudCheckError, match=r"^JSON path 'customer\.age' not found$"
    ):
        response.check.json_path("customer.age", 25)


def test_json_path_raises_when_intermediate_value_is_none():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"customer": None}

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        exceptions.SpudCheckError, match=r"^JSON path 'customer\.age' not found$"
    ):
        response.check.json_path("customer.age", 25)


def test_json_path_accepts_none_as_expected_value():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"customer": None}

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(path="customer", expected=None)


def test_json_checks_array_element():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {
        "orders": [{"id": 101, "status": "created"}, {"id": 102, "status": "paid"}]
    }

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(path="orders[0].status", expected="created")


def test_parse_json_path_with_nested_keys():
    result = parse_json_path("customer.name")
    assert result == ["customer", "name"]


def test_parse_json_path_with_array_index():
    result = parse_json_path("orders[0].status")
    assert result == ["orders", 0, "status"]


def test_json_path_raises_when_index_out_of_range():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"orders": [{"id": 101}]}

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        exceptions.SpudCheckError, match=r"^JSON path 'orders\[5\]\.id' not found$"
    ):
        response.check.json_path(path="orders[5].id", expected=101)


def test_json_path_checks_included_array():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {
        "orders": [{"items": [{"id": 101}, {"id": 102}]}]
    }

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(path="orders[0].items[1].id", expected=102)


def test_json_path_included_matrix():
    result = parse_json_path("matrix[0][1]")
    assert result == ["matrix", 0, 1]


def test_json_path_raises_value_error():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'orders\[abc\]': array index must be an integer$",
    ):
        parse_json_path("orders[abc]")


def test_json_path_raises_with_empty_index():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'orders\[\]': array index cannot be empty$",
    ):
        parse_json_path("orders[]")


def test_json_path_raises_with_unclosed_brackets():
    with pytest.raises(
        ValueError, match=r"^Invalid JSON path 'orders\[0': unclosed bracket$"
    ):
        parse_json_path("orders[0")


def test_json_path_raises_with_unexpected_closing_brackets():
    with pytest.raises(
        ValueError, match=r"^Invalid JSON path 'orders0\]': unexpected closing bracket$"
    ):
        parse_json_path("orders0]")


def test_json_parse_without_separator_after_closing_bracket():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'order\[0\]status': expected separator after closing bracket$",
    ):
        parse_json_path("order[0]status")


def test_json_parse_supports_negative_index():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {
        "orders": [{"id": 101}, {"id": 102}, {"id": 103}]
    }

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(path="orders[-1].id", expected=103)


def test_json_parse_raises_for_negative_index_out_of_range():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {
        "orders": [{"id": 101}, {"id": 102}, {"id": 103}]
    }

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(exceptions.SpudCheckError):
        response.check.json_path(path="orders[-4].id", expected=103)


def test_json_parse_support_omitted_path():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"orders": [{"id": 101}, {"id": 102}]}

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(expected={"orders": [{"id": 101}, {"id": 102}]})


def test_json_parse_raises_without_required_argument():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = {"orders": [{"id": 101}, {"id": 102}]}

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(
        TypeError, match=r"^json_path\(\) missing required argument: expected$"
    ):
        response.check.json_path()


def test_json_parse_raises_with_double_dot_in_path():
    with pytest.raises(
        ValueError, match=r"^Invalid JSON path 'user..name': empty path segment$"
    ):
        parse_json_path("user..name")


def test_json_parse_raises_when_path_ended_with_dot():
    with pytest.raises(
        ValueError, match=r"^Invalid JSON path 'user.': empty path segment$"
    ):
        parse_json_path("user.")


def test_json_parse_raises_when_path_has_bracket_inside_bracket():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'order\[\[0\]\]': unexpected opening bracket$",
    ):
        parse_json_path("order[[0]]")


def test_json_parse_raises_without_separator():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'orders.\[0\]': unexpected opening bracket$",
    ):
        parse_json_path("orders.[0]")


def test_json_parse_with_double_dots():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'orders\[0\]..status': empty path segment$",
    ):
        parse_json_path("orders[0]..status")


def test_json_parse_raises_when_path_starts_with_dot():
    with pytest.raises(
        ValueError, match=r"^Invalid JSON path '.user': empty path segment$"
    ):
        parse_json_path(".user")


def test_json_parse_raises_with_float_in_path():
    with pytest.raises(
        ValueError,
        match=r"^Invalid JSON path 'orders\[0.1\]': array index must be integer$",
    ):
        parse_json_path("orders[0.1]")


def test_json_parse_index_correctly():
    assert parse_json_path("[0]")


@pytest.mark.parametrize(
    "actual, expected",
    [
        ({"active": True}, {"active": 1}),
        ({"users": [{"active": True}]}, ({"users": [{"active": 1}]})),
        (1, 1.0),
    ],
)
def test_json_path_raises_with_type_not_equal(actual, expected):
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = actual

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(exceptions.SpudCheckError):
        response.check.json_path(expected=expected)


@pytest.mark.parametrize(
    "actual, expected",
    [({"users": [{"active": True}]}, ({"users": [{"active": True}]}))],
)
def test_json_path_passes_with_equal_type(actual, expected):
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = actual

    response = api_response.ApiResponse(raw_response_mock)

    response.check.json_path(expected=expected)


@pytest.mark.parametrize("actual, expected", [([1, 2], [1])])
def test_json_path_raises_for_different_list_lengths(actual, expected):
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.json.return_value = actual

    response = api_response.ApiResponse(raw_response_mock)

    with pytest.raises(exceptions.SpudCheckError):
        response.check.json_path(expected=expected)


def test_response_checks_support_method_chaining():
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    raw_response_mock.status_code = 200
    raw_response_mock.json.return_value = {"user": {"name": "Alice"}}

    response = api_response.ApiResponse(raw_response_mock)

    response.check.status(200).json_path("user.name", "Alice")
    response.check.json_path("user.name", "Alice").status(200)


def test_spud_check_error_public_import():
    from spud import SpudCheckError
    from spud.exceptions import SpudCheckError as InternalSpudCheckError

    assert SpudCheckError is InternalSpudCheckError
