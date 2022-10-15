from unittest.mock import Mock, patch

from click.testing import CliRunner
from dynaconf.validator import ValidationError

from gl_search.cli import cli


class TestCustomCommandCollection:
    @patch("gl_search.config.settings.validators.validate_all")
    def test_invoke_command_needs_settings_configured_and_is_not_configured(
        self, mock_validate_all: Mock
    ) -> None:
        error_message = "token not configured"
        mock_validate_all.side_effect = ValidationError(error_message)
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "test"])
        assert result.output == "Settings error: token not configured\n"

    @patch("click.CommandCollection.invoke")
    @patch("gl_search.config.settings.validators.validate_all")
    def test_invoke_command_needs_settings_configured_and_is_configured(
        self, mock_validate_all: Mock, mock_invoke: Mock
    ) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["search", "test"])
        mock_invoke.assert_called_once()

    @patch("click.CommandCollection.invoke")
    @patch("gl_search.config.settings.validators.validate_all")
    def test_invoke_command_not_needs_settings_configured(
        self, mock_validate_all: Mock, mock_invoke: Mock
    ) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["setup-token", "test"])
        mock_invoke.assert_called_once()
        mock_validate_all.assert_not_called()
