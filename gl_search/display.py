import re
from typing import Iterator

from rich.console import Console
from rich.style import Style
from rich.syntax import Syntax

from gl_search.models import RepoResult


class MatchFinder:
    match_position: list[tuple[int, int]]

    def __init__(self, text: str, search_code_input: str) -> None:
        self.match_position = []
        self._process(text, search_code_input)

    def _process(self, text: str, search_code_input: str) -> None:
        splitted_lines = text.split("\n")

        accumulator = 0

        for line, splitted_line in enumerate(splitted_lines, start=1):
            accumulator += len(splitted_line)

            regex_findall_result: Iterator[re.Match[str]] = re.finditer(
                rf"{search_code_input}", splitted_line, flags=re.IGNORECASE
            )

            for match in regex_findall_result:
                self.match_position.append(((line, match.start()), (line, match.end())))


def print_results(results: list[RepoResult], search_code_input: str) -> None:
    console = Console()

    for entry in results:
        if not entry.results:
            continue

        console.print(f"Proj : {entry.name}\n")

        for content in entry.results:
            match_finder = MatchFinder(content.data, search_code_input)

            text = Syntax(
                content.data, content.path.split(".")[-1], start_line=content.start_line, line_numbers=True
            )

            for match_position in match_finder.match_position:
                text.stylize_range(Style(bgcolor="deep_pink4"), *match_position)

            console.print(f"{content.filename} - {entry.web_url}/-/blob/{content.ref}/{content.path}\n")
            console.print(text)
            console.print("-----------\n")
