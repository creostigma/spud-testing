from unittest.mock import Mock

from spud import ApiResponse, response_checks


def test_api_response_lazily_caches_response_checks():
    raw_response_mock = Mock()
    response = ApiResponse(raw_response_mock)
    check = response.check
    assert isinstance(check, response_checks.ResponseChecks)
    assert check.response is response
    assert response.check is check
