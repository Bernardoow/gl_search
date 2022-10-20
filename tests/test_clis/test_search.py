from unittest.mock import Mock, patch

from click.testing import CliRunner

from gl_search.clis.search import search_command
from gl_search.models import SearchParams


class TestSearch:
    @patch("gl_search.clis.search.print_results")
    @patch("gl_search.clis.search.search")
    def test_call_methods(self, mock_search: Mock, mock_print_results: Mock) -> None:
        runner = CliRunner()
        result = runner.invoke(search_command, ["test"])
        assert result.exit_code == 0

        mock_search.assert_called_once()
        mock_print_results.assert_called_once()

    @patch("gl_search.clis.search.print_results")
    @patch("gl_search.clis.search.search")
    def test_params(self, mock_search: Mock, mock_print_results: Mock) -> None:
        group = "1"
        max_workers = "10"
        visibility_one = "internal"
        visibility_two = "private"
        search_code = "test"

        runner = CliRunner()
        params = [
            search_code,
            "-g",
            group,
            "-mw",
            max_workers,
            "-v",
            visibility_one,
            "-v",
            visibility_two,
        ]
        result = runner.invoke(search_command, params)
        assert result.exit_code == 0

        mock_search.assert_called_once_with(
            SearchParams(
                groups=group,
                max_workers=max_workers,
                visibility=[visibility_one, visibility_two],
                search_code_input=search_code,
                max_random_time_for_sleep=5,
            )
        )
        mock_print_results.assert_called_once()
