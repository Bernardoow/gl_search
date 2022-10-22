import re
from typing import Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)
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


class ProcessUserFeedback:
    SEARCHING_GROUPS = "Searching groups"
    SEARCHING_REPOS = "Searching repos"
    SEARCHING_CODE = "Searching code"
    progress: Progress
    _tasks: dict[str, TaskID]

    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
        )

        self._tasks = dict()
        self._add_tasks()

    def _get_task(self, task_name: str) -> TaskID:
        return self._tasks[task_name]

    def set_completed(self, task_name: str) -> None:
        self.progress.update(self._get_task(task_name), completed=True)

    def set_total(self, task_name: str, new_total: float) -> None:
        self.progress.update(self._get_task(task_name), total=new_total)

    def set_advance(self, task_name: str) -> None:
        self.progress.advance(self._get_task(task_name))

    def set_visible(self, task_name: str) -> None:
        self.progress.update(self._get_task(task_name), visible=True)

    def _add_tasks(self) -> None:
        self._tasks[self.SEARCHING_GROUPS] = self.progress.add_task(self.SEARCHING_GROUPS, total=1)
        self._tasks[self.SEARCHING_REPOS] = self.progress.add_task(
            self.SEARCHING_REPOS, total=100, visible=False
        )
        self._tasks[self.SEARCHING_CODE] = self.progress.add_task(
            self.SEARCHING_CODE, total=100, visible=False
        )


process_user_feedback = ProcessUserFeedback()


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
