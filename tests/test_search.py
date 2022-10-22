from http import HTTPStatus
from typing import Optional
from unittest.mock import ANY, Mock, call, patch

import pytest
from pytest_unordered import unordered

from gl_search.models import (
    Repo,
    RepoResult,
    RequestDescribe,
    SearchEntryResult,
    SearchParams,
    SearchRepoParams,
)
from gl_search.search import (
    _retrieve_groups_ids,
    _retrieve_information_from_repositories_of_each_group,
    _retrieve_repositories_by,
    _search_code,
    _search_in_repo,
    search,
)

from .utils import build_response


@pytest.fixture
def search_params() -> SearchParams:
    return SearchParams(
        search_code_input="search", max_workers=5, visibility=["private"], max_random_time_for_sleep=5
    )


class TestSearchCode:
    @patch("gl_search.search._search_in_repo")
    def test_it_should_search_on_gl(self, mock_search_in_repo: Mock, search_params: SearchParams) -> None:
        repo_name_1 = "test_1"
        repo_name_2 = "test_2"
        repo_name_3 = "test_3"
        web_url_1 = "url1"
        web_url_2 = "url2"
        web_url_3 = "url3"
        result_1 = SearchEntryResult(
            path="path_1", filename="filename_1", project_id=1, data="data_1", startline=1, ref="main"
        )
        result_2 = SearchEntryResult(
            path="path_2", filename="filename_2", project_id=2, data="data_2", startline=1, ref="main"
        )
        result_3 = SearchEntryResult(
            path="path_3", filename="filename_3", project_id=3, data="data_3", startline=1, ref="main"
        )
        mock_search_in_repo.side_effect = [[result_1], [result_2], [result_3]]
        repo_list: list[Repo] = [
            Repo(id=1, name=repo_name_1, visibility="public", web_url=web_url_1),
            Repo(id=2, name=repo_name_2, visibility="public", web_url=web_url_2),
            Repo(id=3, name=repo_name_3, visibility="public", web_url=web_url_3),
        ]
        response = _search_code(repo_list, search_params)

        assert mock_search_in_repo.call_count == len(repo_list)
        assert response == unordered(
            [
                RepoResult(**{"name": repo_name_1, "results": [result_1], "web_url": web_url_1}),
                RepoResult(**{"name": repo_name_2, "results": [result_2], "web_url": web_url_2}),
                RepoResult(**{"name": repo_name_3, "results": [result_3], "web_url": web_url_3}),
            ]
        )

    @pytest.mark.parametrize("max_workers", (5, 50))
    @patch("concurrent.futures.as_completed", Mock(return_value=[]))
    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_mx_workers(
        self, mock_thread_pool_executor: Mock, max_workers: int, search_params: SearchParams
    ) -> None:
        search_params.max_workers = max_workers
        _search_code([], search_params)
        mock_thread_pool_executor.assert_called_with(max_workers=max_workers)


class TestSearchInRepo:
    @patch("gl_search.search.retrieve_data")
    def test_check_url(self, mock_retrieve_data: Mock, search_params: SearchParams) -> None:
        repo_id = 1

        _search_in_repo(SearchRepoParams(repo_id=repo_id, **search_params.dict()))

        request_describe = RequestDescribe(
            url=f"https://gitlab.com/api/v4/projects/{repo_id}/search",
            params={"scope": "blobs", "search": search_params.search_code_input, "per_page": "100"},
        )
        mock_retrieve_data.assert_called_with(
            request_describe, ANY, max_random_time_for_sleep=search_params.max_random_time_for_sleep
        )

    @patch("requests.get")
    def test_it_should_return_sentry_entry_result_list(
        self, mock_requests_get: Mock, search_params: SearchParams
    ) -> None:
        mock_requests_get.return_value = build_response(
            HTTPStatus.OK,
            [
                {
                    "path": "path_1",
                    "filename": "filename_1",
                    "project_id": 1,
                    "data": "data_1",
                    "ref": "main",
                    "startline": 10,
                }
            ],
        )

        response = _search_in_repo(SearchRepoParams(repo_id=1, **search_params.dict()))
        assert response == [
            SearchEntryResult(
                path="path_1", filename="filename_1", project_id=1, data="data_1", ref="main", startline=10
            )
        ]


class TestRetrieveInformationFromRepositoriesOfEachGroup:
    @patch("gl_search.search._retrieve_repositories_by")
    def test_it_should_search_each_repo_on_the_list(
        self, mock_retrieve_repositories_by: Mock, search_params: SearchParams
    ) -> None:
        search_params.visibility = []
        _retrieve_information_from_repositories_of_each_group([1, 2, 3], search_params)
        assert mock_retrieve_repositories_by.call_args_list == [
            call(1, search_params),
            call(2, search_params),
            call(3, search_params),
        ]

    @patch("gl_search.search._retrieve_repositories_by")
    def test_visibility_choose(self, mock_set_repos_by_group: Mock, search_params: SearchParams) -> None:
        search_params.visibility = ["public"]
        _retrieve_information_from_repositories_of_each_group([1], search_params)
        assert mock_set_repos_by_group.call_args_list == [
            call(1, search_params),
        ]

    @patch("gl_search.search._retrieve_repositories_by")
    def test_repo_info_should_be_unique(
        self, mock_retrieve_repositories_by: Mock, search_params: SearchParams
    ) -> None:
        mock_retrieve_repositories_by.side_effect = [{1, 2, 3}, {3, 4, 5}, {4, 5, 6}]
        repo_set = _retrieve_information_from_repositories_of_each_group([1, 2, 3], search_params)
        assert mock_retrieve_repositories_by.call_args_list == [
            call(1, search_params),
            call(2, search_params),
            call(3, search_params),
        ]
        assert repo_set == {1, 2, 3, 4, 5, 6}

    @pytest.mark.parametrize("max_workers", (5, 50))
    @patch("concurrent.futures.as_completed", Mock(return_value=[]))
    @patch("concurrent.futures.ThreadPoolExecutor")
    def test_mx_workers(
        self, mock_thread_pool_executor: Mock, max_workers: int, search_params: SearchParams
    ) -> None:
        search_params.max_workers = max_workers
        _retrieve_information_from_repositories_of_each_group([1, 2, 3], search_params)
        mock_thread_pool_executor.assert_called_with(max_workers=max_workers)


class TestRetrieveRepositoriesBy:
    @pytest.mark.parametrize(
        "group_id, visibilities",
        ((1, ["internal", "public", "private"]), (2, ["private"])),
    )
    @patch("gl_search.search.retrieve_data")
    def test_it_should_retrieve_group_and_each_visibility(
        self, mock_retrieve_data: Mock, group_id: int, visibilities: list[str], search_params: SearchParams
    ) -> None:

        search_params.visibility = visibilities

        _retrieve_repositories_by(group_id, search_params)
        mock_retrieve_data.assert_called_once_with(
            RequestDescribe(
                url=f"https://gitlab.com/api/v4/groups/{group_id}/projects",
                params={
                    "include_subgroups": "true",
                    "per_page": "100",
                },
            ),
            ANY,
            max_random_time_for_sleep=search_params.max_random_time_for_sleep,
        )

    @patch("requests.get")
    def test_it_should_return_repo_item(self, mock_requests_get: Mock, search_params: SearchParams) -> None:
        mock_requests_get.return_value = build_response(
            HTTPStatus.OK,
            [
                {"id": 1, "name": "test 1", "visibility": "private", "web_url": "url_1"},
                {"id": 2, "name": "test 2", "visibility": "private", "web_url": "url_2"},
            ],
        )
        search_params.visibility = ["private"]
        response: set[Repo] = _retrieve_repositories_by(1, search_params)

        assert response == {
            Repo(id=1, name="test 1", visibility="private", web_url="url_1"),
            Repo(id=2, name="test 2", visibility="private", web_url="url_2"),
        }


class TestRetrieveGroupsIds:
    @patch("gl_search.search.retrieve_data")
    def test_it_should_retrieve_from_gl(self, mock_retrieve_data: Mock, search_params: SearchParams) -> None:
        _retrieve_groups_ids(search_params)

        mock_retrieve_data.assert_called_once_with(
            RequestDescribe(
                url="https://gitlab.com/api/v4/groups",
                params={
                    "pagination": "keyset",
                    "order_by": "id",
                    "sort": "asc",
                    "per_page": "100",
                },
            ),
            ANY,
            max_random_time_for_sleep=search_params.max_random_time_for_sleep,
        )

    @patch("requests.get")
    def test_it_should_return_int_list(self, mock_requests_get: Mock, search_params: SearchParams) -> None:
        mock_requests_get.return_value = build_response(HTTPStatus.OK, [{"id": 1}, {"id": 2}])
        response: list[int] = _retrieve_groups_ids(search_params)

        assert response == [1, 2]


class TestSearch:
    @pytest.mark.parametrize(
        "groups, expected",
        ((None, "assert_called_once_with"), ("1,2", "assert_not_called")),
    )
    @patch("gl_search.search._search_code")
    @patch("gl_search.search._retrieve_information_from_repositories_of_each_group")
    @patch("gl_search.search._retrieve_groups_ids")
    def test_call_methods(
        self,
        mock_retrieve_groups_ids: Mock,
        mock_retrieve_information_from_repositories_of_each_group: Mock,
        mock_search_code: Mock,
        groups: Optional[str],
        expected: str,
    ) -> None:
        repo_test_1 = Repo(id=3, name="repo_1", visibility="public", web_url="url")
        repo_test_2 = Repo(id=4, name="repo_2", visibility="public", web_url="url")
        mock_retrieve_groups_ids.return_value = [1, 2]
        mock_retrieve_information_from_repositories_of_each_group.return_value = {
            repo_test_1,
            Repo(id=4, name="repo_2", visibility="public", web_url="url"),
        }
        mock_search_code.return_value = [{"name": "repo_1", "content": "content"}]

        params = SearchParams(
            groups=groups,
            search_code_input="test",
            max_workers=1,
            visibility=["public"],
            max_random_time_for_sleep=5,
        )
        result = search(params)
        if not groups:
            getattr(mock_retrieve_groups_ids, expected)(params)
        else:
            getattr(mock_retrieve_groups_ids, expected)()

        mock_retrieve_information_from_repositories_of_each_group.assert_called_once_with([1, 2], params)
        mock_search_code.assert_called_once_with(
            {
                repo_test_2,
                repo_test_1,
            },
            params,
        )
        assert [entry.keys() for entry in result] == [{"name", "content"}]
