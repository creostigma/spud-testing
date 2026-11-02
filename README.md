# SPUD
Stop planting the same test framework over and over again.

Spud is a Python testing framework for QA engineers who don't want to rebuild the same setup every time they join a new project.

It comes with the stuff you usually end up writing anyway, but doesn't lock you into one way of doing things. Use what you need, replace what you don't, or build on top of it.

Plant once. Grow tests.

## Installation
```bash
pip install spud-testing
```

## Quick start
```python
from spud import ApiClient

client = ApiClient(base_url="https://jsonplaceholder.typicode.com")

response = client.get("/users/1")

response.check.status(200).json_path("id", 1)

print(response.json())
```

## Features
- HTTP methods: GET, POST, PUT, PATCH, DELETE
- Configurable base URL and request headers
- Query parameters and JSON request bodies
- Pluggable HTTP transport (httpx by default)
- HTTP status assertions
- JSON path assertions with nested objects and arrays
- Strict JSON value comparison
- Chainable response assertions
