from unittest.mock import Mock, create_autospec

import pytest

from spud import api_client, httpx_transport, raw_response_protocol, transport_protocol
from spud.api_response import ApiResponse
from spud.raw_response_protocol import RawResponseProtocol
from spud.transport_protocol import TransportProtocol


@pytest.mark.parametrize("base_url", ["http://google.com/", "http://google.com///"])
def test_base_url_removes_trailing_slash(base_url):
    transport = create_autospec(spec=TransportProtocol, instance=True)
    client = api_client.ApiClient(base_url, transport)
    assert client.base_url == "http://google.com"


def test_get_raises_value_error_when_path_has_no_leading_slash():
    transport = create_autospec(spec=TransportProtocol, instance=True)
    client = api_client.ApiClient("http://google.com", transport)
    with pytest.raises(ValueError):
        client.get("search")
    transport.request.assert_not_called()


def test_get_delegates_to_transport():
    headers = {"Authorization": "Bearer Token..."}
    params = {"q": 123}
    fake_raw_response = object()
    transport = create_autospec(spec=TransportProtocol, instance=True)
    client = api_client.ApiClient("http://google.com", transport)
    transport.request.return_value = fake_raw_response
    response = client.get("/search", params=params, headers=headers)
    assert response.raw is fake_raw_response
    transport.request.assert_called_once_with(
        method="GET",
        url="http://google.com/search",
        params=params,
        headers=headers,
        json=None,
    )


def test_post_delegates_to_transport():
    json = {"name": "Ruslan", "age": 30}
    headers = {"Authorization": "Bearer token"}
    fake_raw_response = object()
    transport = create_autospec(spec=TransportProtocol, instance=True)
    client = api_client.ApiClient("http://google.com", transport)
    transport.request.return_value = fake_raw_response
    response = client.post("/create", json=json, headers=headers)
    assert response.raw is fake_raw_response
    transport.request.assert_called_once_with(
        method="POST",
        url="http://google.com/create",
        json=json,
        headers=headers,
        params=None,
    )


def test_status_code_returns_raw_response_status_code():
    status_code = 201
    raw_response_mock = Mock(spec=RawResponseProtocol)
    raw_response_mock.status_code = status_code
    response = ApiResponse(raw_response_mock)
    assert status_code == response.status_code


def test_headers_returns_raw_response_headers():
    headers = {"Authorization": "Bearer token"}
    raw_response_mock = Mock(spec=RawResponseProtocol)
    raw_response_mock.headers = headers
    response = ApiResponse(raw_response_mock)
    assert headers == response.headers


def test_text_returns_raw_response_text():
    text = "text"
    raw_response_mock = Mock(spec=RawResponseProtocol)
    raw_response_mock.text = text
    response = ApiResponse(raw_response_mock)
    assert text == response.text


def test_json_returns_raw_response_json():
    json = {"name": "Ruslan", "age": 30}
    raw_response_mock = Mock(spec=RawResponseProtocol)
    raw_response_mock.json.return_value = json
    response = ApiResponse(raw_response_mock)
    assert json == response.json()


@pytest.mark.parametrize(
    "method_name, expected_method, kwargs",
    [
        (
            "post",
            "POST",
            {"json": {"status": "ok"}, "headers": {"Authorization": "Bearer token"}},
        ),
        (
            "get",
            "GET",
            {"params": {"q": 123}, "headers": {"Authorization": "Bearer token"}},
        ),
        (
            "put",
            "PUT",
            {"json": {"status": "ok"}, "headers": {"Authorization": "Bearer token"}},
        ),
        (
            "patch",
            "PATCH",
            {"json": {"status": "ok"}, "headers": {"Authorization": "Bearer token"}},
        ),
        (
            "delete",
            "DELETE",
            {"headers": {"Authorization": "Bearer token"}, "params": {"q": 123}},
        ),
    ],
)
def test_method_deligates_to_transport(method_name, expected_method, kwargs):
    transport = create_autospec(spec=TransportProtocol, instance=True)
    raw_response_mock = Mock(spec=RawResponseProtocol)
    transport.request.return_value = raw_response_mock
    client = api_client.ApiClient("http://google.com", transport)
    method = getattr(client, method_name)
    response = method(path="/search", **kwargs)
    transport.request.assert_called_once_with(
        method=expected_method,
        url="http://google.com/search",
        json=kwargs.get("json"),
        headers=kwargs.get("headers"),
        params=kwargs.get("params"),
    )
    assert response.raw is raw_response_mock


def test_request_with_default_transport():
    client = api_client.ApiClient("http://google.com")
    assert isinstance(client.transport, httpx_transport.HttpxTransport)


def test_api_client_uses_default_headers():
    transport = create_autospec(
        spec=transport_protocol.TransportProtocol, instance=True
    )
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    transport.request.return_value = raw_response_mock
    headers = {"Authorization": "Bearer abc"}
    client = api_client.ApiClient(
        "http://google.com", transport=transport, headers=headers
    )
    client.get("/orders")
    transport.request.assert_called_once_with(
        method="GET",
        url="http://google.com/orders",
        params=None,
        headers=headers,
        json=None,
    )


def test_request_headers_override_and_extend_default_headers():
    transport = create_autospec(
        spec=transport_protocol.TransportProtocol, instance=True
    )
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    transport.request.return_value = raw_response_mock
    headers = {"Authorization": "Bearer abc", "X-App": "Mobile"}
    request_headers = {"X-Request-ID": "123", "X-App": "Web"}
    expected_headers = {
        "Authorization": "Bearer abc",
        "X-Request-ID": "123",
        "X-App": "Web",
    }
    client = api_client.ApiClient(
        "http://google.com", transport=transport, headers=headers
    )
    client.get("/orders", headers=request_headers)
    transport.request.assert_called_once_with(
        method="GET",
        url="http://google.com/orders",
        params=None,
        headers=expected_headers,
        json=None,
    )
