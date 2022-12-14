import pytest

from gl_search.models import SearchRepoParams


class TestSearchRepoParams:
    @pytest.mark.parametrize(
        "params, expected",
        [
            ({"extension": "py"}, "test extension:py"),
            ({"filename": "test"}, "test filename:test"),
            ({"path": "test"}, "test path:test"),
        ],
    )
    def test_search_with_params(self, params: str, expected: str):

        search_params = SearchRepoParams(
            repo_id=1, search_code_input="test", max_random_time_for_sleep=5, **params
        )
        assert search_params.search_with_params == expected
