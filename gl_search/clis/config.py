from typing import Any

import click
import toml

from gl_search.config import BLOCK_SETTINGS_NAME, SETTINGS_FILE_PATH


@click.group("settings")
def config_cli() -> None:
    ...


def _load_settings(file_path: str) -> dict[str, Any]:
    try:
        current_settings = toml.load(file_path)
    except FileNotFoundError:
        current_settings = {BLOCK_SETTINGS_NAME: {}}

    return current_settings


def _write_settings(file_path: str, current_settings: dict[str, Any]) -> None:
    with open(file_path, "w") as file:
        toml.dump(current_settings, file)


@config_cli.command(name="setup-token", short_help="Command to register the token to be used with requests.")
@click.argument("token")
def setup_token(token: str) -> None:
    """This command register the TOKEN that going to be used with requests.

    The TOKEN is generate on your gitlab profile [1] with scope read_api.

    [1] https://gitlab.com/-/profile/personal_access_tokens

    """

    current_settings = _load_settings(SETTINGS_FILE_PATH)
    current_settings[BLOCK_SETTINGS_NAME].update({"GITLAB_PRIVATE_TOKEN": token})

    _write_settings(SETTINGS_FILE_PATH, current_settings)

    click.secho("Successfully registered.", fg="green")


@config_cli.command(
    name="setup-gitlab-address", short_help="Command to register the gitlab address to be used with requests."
)
@click.argument("address")
def setup_gitlab_address(address: str) -> None:
    """This command register the address that going to be used with requests."""

    current_settings = _load_settings(SETTINGS_FILE_PATH)
    current_settings[BLOCK_SETTINGS_NAME].update({"GITLAB_URL": address})

    _write_settings(SETTINGS_FILE_PATH, current_settings)

    click.secho("Successfully registered.", fg="green")
