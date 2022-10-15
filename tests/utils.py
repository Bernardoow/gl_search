from http import HTTPStatus
from typing import Any
from unittest.mock import Mock

from requests import Response


def build_response(status_code: HTTPStatus, json_return: Any) -> None:
    response = Mock(spec=Response)
    response.status_code = status_code
    response.json.return_value = json_return
    response.links = {}
    return response
