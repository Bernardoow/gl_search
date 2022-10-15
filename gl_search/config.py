import os
from typing import Final

from dynaconf import Dynaconf, Validator

BLOCK_SETTINGS_NAME: Final[str] = "gl-settings"

SETTINGS_FILE_PATH: Final[str] = f"{os.path.expanduser('~')}/.gl-settings.toml"
settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    settings_files=[SETTINGS_FILE_PATH],
    environments=[BLOCK_SETTINGS_NAME],
    default_env=BLOCK_SETTINGS_NAME,
    validators=[
        Validator("GITLAB_URL", default="https://gitlab.com"),
        Validator("MAX_DEEP_SEARCH", default=1000),
    ],
)

settings.validators.register(
    Validator(
        "GITLAB_PRIVATE_TOKEN",
        must_exist=True,
        messages={
            "must_exist_true": "You must register your token.",
            "operations": "You must register your token.",
        },
    )
)
