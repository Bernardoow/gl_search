import click
from click import CommandCollection
from dynaconf.validator import ValidationError

from .clis import config_cli, search_cli
from .config import settings


class CustomCommandCollection(CommandCollection):
    def invoke(self, ctx):
        args = [*ctx.protected_args, *ctx.args]
        cmd_name, cmd, args = self.resolve_command(ctx, args)

        COMMANDS_THAT_NEED_THE_LIBRARY_CONFIGURED = ["search"]

        if cmd_name in COMMANDS_THAT_NEED_THE_LIBRARY_CONFIGURED:
            try:
                settings.validators.validate_all()
            except ValidationError as error:
                click.secho(f"Settings error: {error}", fg="red")
                ctx.exit()
        return super().invoke(ctx)


cli = CustomCommandCollection(name="gl-search", sources=[search_cli, config_cli])
