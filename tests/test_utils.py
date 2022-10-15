from copy import deepcopy
from http import HTTPStatus
from unittest.mock import ANY, Mock, call, patch

import pytest
from pytest_unordered import unordered

from gl_search.models import RequestDescribe
from gl_search.utils import retrieve_data

from .utils import build_response


class TestRetrieveData:
    @patch("time.sleep")
    @patch("requests.get")
    def test_it_should_call_url(self, mock_request_get: Mock, mock_time_sleep: Mock) -> None:
        url = "https://example.com/"
        url_2 = f"{url}page=2"

        time_for_sleep = 10

        response = build_response(HTTPStatus.OK, {})
        response._count_links = 0
        response.links = {"next": {"url": url_2}}

        response_2 = build_response(HTTPStatus.OK, {})
        mock_request_get.side_effect = [response, response_2]
        request_describe = RequestDescribe(url=url)

        retrieve_data(deepcopy(request_describe), lambda: None, time_for_sleep)

        assert list(mock_request_get.call_args_list) == unordered(
            [
                call(request_describe.url, params={}, headers=ANY, timeout=time_for_sleep),
                call(url_2, params={}, headers=ANY, timeout=time_for_sleep),
            ]
        )
        mock_time_sleep.assert_called_once_with(time_for_sleep)

    @patch("requests.get")
    def test_it_should_raise_exception_when_get_invalid_status_code(self, mock_requests_get: Mock) -> None:
        mock_requests_get.return_value = build_response(HTTPStatus.BAD_REQUEST, {})

        with pytest.raises(Exception, match=r"invalid status code"):
            retrieve_data(RequestDescribe(url="https://example.com/"), lambda: None, 10)
