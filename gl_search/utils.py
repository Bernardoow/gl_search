import time
from http import HTTPStatus
from typing import Callable, Final

import requests

from .config import settings
from .models import RequestDescribe


def retrieve_data(
    request: RequestDescribe,
    transform_data: Callable = lambda value: value,
    time_for_sleep: float = 0,
) -> list:
    count: int = 0
    data_list: list[dict] = []
    HEADERS: Final[dict[str, str]] = {"PRIVATE-TOKEN": settings.GITLAB_PRIVATE_TOKEN}
    while True or count < settings.MAX_DEEP_SEARCH:
        count += 1
        response: requests.Response = requests.get(
            request.url, params=request.params, headers=HEADERS, timeout=10
        )

        if not response.status_code == HTTPStatus.OK:
            raise Exception(f"invalid status code {response.status_code}")

        data_list.extend([transform_data(data) for data in response.json()])

        try:
            request.url: str = response.links["next"]["url"]
            request.params = {}
        except KeyError:
            break

        time.sleep(time_for_sleep)

    return data_list
