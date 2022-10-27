import contextlib
from copy import deepcopy
from http import HTTPStatus
from random import uniform
from unittest.mock import ANY, Mock, call, patch

import pytest
from pytest_unordered import unordered

from gl_search.models import RequestDescribe
from gl_search.utils import retrieve_data

from .utils import build_response


class TestRetrieveData:
    @patch("gl_search.utils.uniform")
    @patch("time.sleep")
    @patch("gl_search.utils.request_session.get")
    def test_it_should_call_url(
        self, mock_request_get: Mock, mock_time_sleep: Mock, mock_uniform: Mock
    ) -> None:
        url = "https://example.com/"
        url_2 = f"{url}page=2"

        max_random_time_for_sleep = 10
        uniform_response = uniform(0, max_random_time_for_sleep)

        response = build_response(HTTPStatus.OK, {})
        response._count_links = 0
        response.links = {"next": {"url": url_2}}

        response_2 = build_response(HTTPStatus.OK, {})
        mock_request_get.side_effect = [response, response_2]
        mock_uniform.return_value = uniform_response
        request_describe = RequestDescribe(url=url)

        retrieve_data(deepcopy(request_describe), lambda: None, max_random_time_for_sleep)

        assert list(mock_request_get.call_args_list) == unordered(
            [
                call(request_describe.url, params={}, timeout=max_random_time_for_sleep),
                call(url_2, params={}, timeout=max_random_time_for_sleep),
            ]
        )
        mock_time_sleep.assert_called_once_with(uniform_response)

    @patch("gl_search.utils.request_session.get")
    def test_it_should_raise_exception_when_get_invalid_status_code(self, mock_requests_get: Mock) -> None:
        mock_requests_get.return_value = build_response(HTTPStatus.BAD_REQUEST, {})

        with pytest.raises(Exception, match=r"invalid status code"):
            retrieve_data(RequestDescribe(url="https://example.com/"), lambda: None, 10)

    @patch("gl_search.utils.process_user_feedback")
    @patch("gl_search.utils.logger")
    @patch("requests.get")
    def test_it_should_log(
        self, mock_requests_get: Mock, mock_logger: Mock, mock_process_user_feedback: Mock
    ) -> None:
        mock_requests_get.return_value = build_response(HTTPStatus.BAD_REQUEST, {})

        mock_logger.isEnabledFor.return_value = True

        url = "https://example.com/"
        with contextlib.suppress(Exception):
            retrieve_data(RequestDescribe(url=url), lambda: None, 10)

        mock_process_user_feedback.progress.log.assert_called_with("URL: {} PARAMS: {}".format(url, dict()))
