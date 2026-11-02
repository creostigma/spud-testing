from unittest.mock import Mock, create_autospec

import pytest

from spud import (
    api_client,
    api_response,
    endpoint,
    raw_response_protocol,
    transport_protocol,
)


def test_endpoint_stores_provided_api_client():
    client = api_client.ApiClient(base_url="https://google.com")
    endpoint_test = endpoint.Endpoint(client=client)
    assert endpoint_test.client is client


def test_endpoint_subclass_requires_path():
    with pytest.raises(TypeError):

        class BrokenEndpoint(endpoint.Endpoint):
            pass


def test_endpoint_path_must_be_string():
    with pytest.raises(TypeError):

        class BrokenEndpoint(endpoint.Endpoint):
            path = 123


def test_endpoint_subclass_has_inherits_path():
    class OrdersEndpoint(endpoint.Endpoint):
        path = "/orders"

    class EndpointSubclass(OrdersEndpoint):
        pass

    assert EndpointSubclass.path == OrdersEndpoint.path


def test_usability():
    class OrdersEndpoint(endpoint.Endpoint):
        path = "/orders"

        def get_order(self, order_id):
            path = self.path + "/" + order_id
            response = self.client.get(path=path)
            return response

    transport = create_autospec(
        spec=transport_protocol.TransportProtocol, instance=True
    )
    raw_response_mock = Mock(spec=raw_response_protocol.RawResponseProtocol)
    transport.request.return_value = raw_response_mock
    client = api_client.ApiClient(base_url="http://google.com", transport=transport)
    orders = OrdersEndpoint(client)
    response = orders.get_order("123")
    transport.request.assert_called_once_with(
        method="GET",
        url="http://google.com/orders/123",
        params=None,
        headers=None,
        json=None,
    )
    assert isinstance(response, api_response.ApiResponse)
    assert response.raw is raw_response_mock
