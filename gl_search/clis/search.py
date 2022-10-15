from typing import Optional

import click

from gl_search.display import print_results
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
@click.argument("search_code_input")
def search_command(
    groups: Optional[str],
    search_code_input: str,
    max_workers: int,
    visibility: list[str],
    extension: Optional[str],
    filename: Optional[str],
    path: Optional[str],
) -> None:
    """Search command."""
    results: list[dict[str, str]] = search(
        SearchParams(
            groups=groups,
            search_code_input=search_code_input,
            max_workers=max_workers,
            visibility=visibility,
            extension=extension,
            filename=filename,
            path=path,
        )
    )

    print_results(results, search_code_input)
