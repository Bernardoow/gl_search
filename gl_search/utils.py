import logging
import time
from http import HTTPStatus
from random import uniform
from typing import Callable, Final

import requests

from .config import settings
from .display import process_user_feedback
from .models import RequestDescribe

logger = logging.getLogger(__name__)


def retrieve_data(
    request: RequestDescribe,
    transform_data: Callable = lambda value: value,
    max_random_time_for_sleep: float = 0,
) -> list:
    count: int = 0
    data_list: list[dict] = []
    HEADERS: Final[dict[str, str]] = {"PRIVATE-TOKEN": settings.GITLAB_PRIVATE_TOKEN}
    while True or count < settings.MAX_DEEP_SEARCH:
        count += 1

        if logger.isEnabledFor(logging.DEBUG):
            process_user_feedback.progress.log("URL: {} PARAMS: {}".format(request.url, request.params))

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

        time.sleep(uniform(0, max_random_time_for_sleep))

    return data_list
