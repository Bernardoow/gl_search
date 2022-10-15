import re
from unittest.mock import ANY, Mock, call, patch

from gl_search.display import MatchFinder, print_results
from gl_search.models import RepoResult, SearchEntryResult


class TestMatchFinder:
    def test_process(self):
        text = "test\nanother\ntest"
        match_finder = MatchFinder(text, "test")
        assert match_finder.match_position == [((1, 0), (1, 4)), ((3, 0), (3, 4))]


class TestPrintResults:
    @patch("gl_search.display.Console")
    def test_when_have_not_project(self, mock_console: Mock) -> None:
        print_results({}, "test")
        mock_console.return_value.print.assert_not_called()

    @patch("gl_search.display.Console")
    def test_when_have_project_without_content(self, mock_console: Mock) -> None:
        proj_1 = "test 1"
        proj_2 = "test 2"
        data = [
            RepoResult(**{"name": proj_1, "content": [], "web_url": "url_1"}),
            RepoResult(**{"name": proj_2, "content": [], "web_url": "url_1"}),
        ]
        print_results(data, "test")
        mock_console.assert_called()
        mock_console.return_value.print.assert_not_called()

    @patch("re.finditer")
    @patch("gl_search.display.Style")
    @patch("gl_search.display.Syntax")
    @patch("gl_search.display.Console")
    def test_when_have_content(
        self, mock_console: Mock, mock_syntax: Mock, mock_style: Mock, mock_re_finditer: Mock
    ) -> None:
        proj_1 = "test 1"
        data_input = "this is content to the test."
        data = [
            RepoResult(
                **{
                    "name": proj_1,
                    "results": [
                        SearchEntryResult(
                            path="test.py",
                            filename="test.py",
                            project_id=1,
                            data=data_input,
                            startline=0,
                            ref="main",
                        )
                    ],
                    "web_url": "url",
                }
            )
        ]

        search_code = "test"

        match_re_start = 10
        match_re_end = 15
        match_re = Mock()
        match_re.start.return_value = match_re_start
        match_re.end.return_value = match_re_end

        mock_re_finditer.return_value = [match_re]
        print_results(data, search_code)
        mock_console.assert_called()
        mock_console.return_value.print.assert_called()
        mock_re_finditer.assert_called_once_with(search_code, data_input, flags=re.IGNORECASE)
        mock_syntax.assert_called_once_with(data_input, "py", start_line=0, line_numbers=True)
        mock_style.assert_called_once_with(bgcolor="deep_pink4")

        mock_syntax.return_value.stylize_range.assert_called_once_with(
            ANY, (1, match_re_start), (1, match_re_end)
        )
