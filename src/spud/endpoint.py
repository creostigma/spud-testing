from . import api_client


class Endpoint:
    path: str

    def __init__(self, client: api_client.ApiClient) -> None:
        self.client = client

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "path"):
            raise TypeError("Endpoint subclass must define 'path'")
        if not isinstance(cls.path, str):
            raise TypeError("Endpoint path must be a string")
