import logging
import time
from http import HTTPStatus
from random import uniform
from typing import Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .config import settings
from .display import process_user_feedback
from .models import RequestDescribe

logger = logging.getLogger(__name__)

retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ],
    raise_on_status=False,
)

request_session = requests.Session()

request_session.mount("http://", HTTPAdapter(max_retries=retries))
request_session.mount("https://", HTTPAdapter(max_retries=retries))

request_session.headers.update({"PRIVATE-TOKEN": settings.GITLAB_PRIVATE_TOKEN})


def retrieve_data(
    request: RequestDescribe,
    transform_data: Callable = lambda value: value,
    max_random_time_for_sleep: float = 0,
) -> list:
    count: int = 0
    data_list: list[dict] = []
    while True or count < settings.MAX_DEEP_SEARCH:
        count += 1

        if logger.isEnabledFor(logging.DEBUG):
            process_user_feedback.progress.log("URL: {} PARAMS: {}".format(request.url, request.params))

        response: requests.Response = request_session.get(request.url, params=request.params, timeout=10)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            process_user_feedback.progress.print(
                "URL: {} PARAMS: {} HttpStatus Code 429 SKIP this search".format(request.url, request.params)
            )
            break
        elif not response.status_code == HTTPStatus.OK:
            raise Exception(f"invalid status code {response.status_code}")

        data_list.extend([transform_data(data) for data in response.json()])

        try:
            request.url: str = response.links["next"]["url"]
            request.params = {}
        except KeyError:
            break

        time.sleep(uniform(0, max_random_time_for_sleep))

    return data_list
