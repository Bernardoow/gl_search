import logging
from typing import Optional

import click

from gl_search.display import print_results, process_user_feedback
from gl_search.models import SearchParams
from gl_search.search import search


@click.group()
def search_cli() -> None:
    ...


@search_cli.command(name="search")
@click.option("-p", "--path", default=None, help="search by Path")
@click.option("-fn", "--filename", default=None, help="search by filename")
@click.option("-ext", "--extension", default=None, help="code filename extension :: py,js,cs")
@click.option("-g", "--groups", default=None, help="search by gitlab group")
@click.option("-mw", "--max-workers", default=5, type=int, help="number of parallel requests")
@click.option(
    "-v",
    "--visibility",
    type=click.Choice(["internal", "public", "private"], case_sensitive=False),
    multiple=True,
    default=["internal", "public", "private"],
    help="repositories visibility",
)
@click.option("-xdr", "--max-delay-request", default=5, type=int, help="max delay request")
@click.option(
    "-d", "--debug", is_flag=True, show_default=True, default=False, help="Debug :: show urls called."
)
@click.argument("search_code_input")
def search_command(
    groups: Optional[str],
    search_code_input: str,
    max_workers: int,
    visibility: list[str],
    extension: Optional[str],
    filename: Optional[str],
    path: Optional[str],
    max_delay_request: int,
    debug: bool,
) -> None:
    """Search command."""
    if debug:
        logger = logging.getLogger("gl_search")
        logger.setLevel(logging.DEBUG)

    with process_user_feedback.progress:
        results: list[dict[str, str]] = search(
            SearchParams(
                groups=groups,
                search_code_input=search_code_input,
                max_workers=max_workers,
                visibility=visibility,
                extension=extension,
                filename=filename,
                path=path,
                max_random_time_for_sleep=max_delay_request,
            )
        )

    print_results(results, search_code_input)
