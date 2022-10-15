from copy import deepcopy
from unittest.mock import ANY, Mock, patch

import toml
from click.testing import CliRunner

from gl_search.clis.config import _load_settings, _write_settings, setup_gitlab_address, setup_token


class TestLoadSettings:
    def test_when_file_is_not_found(self) -> None:
        assert _load_settings("./.file-not-exist.toml") == {"gl-settings": {}}

    def test_when_file_is_found(self) -> None:
        file_path = "./.click-settings-file.toml"
        runner = CliRunner()
        data = {"gl-settings": {"GITLAB_PRIVATE_TOKEN": "token"}}
        with runner.isolated_filesystem():
            with open(file_path, "w") as f:
                toml.dump(data, f)

            assert data == _load_settings(file_path)


class TestWriteSettings:
    def test_when_is_writing_file(self) -> None:
        data = {"gl-settings": {}}
        file_path = "./.click-settings-file.toml"
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_settings(file_path, data)
            assert _load_settings(file_path) == data


class TestSetupToken:
    @patch("gl_search.clis.config._load_settings")
    @patch("gl_search.clis.config._write_settings")
    def test_call_methods(self, mock_write_settings: Mock, mock_load_settings: Mock) -> None:
        runner = CliRunner()
        result = runner.invoke(setup_token, ["token"])
        assert result.exit_code == 0
        assert result.output == "Successfully registered.\n"
        mock_load_settings.assert_called_once()
        mock_write_settings.assert_called_once()

    @patch("gl_search.clis.config._load_settings")
    @patch("gl_search.clis.config._write_settings")
    def test_add_token(self, mock_write_settings: Mock, mock_load_settings: Mock) -> None:
        environment = "gl-settings"
        data = {environment: {}}
        mock_load_settings.return_value = deepcopy(data)
        runner = CliRunner()
        result = runner.invoke(setup_token, ["token"])
        assert result.exit_code == 0
        assert result.output == "Successfully registered.\n"

        data[environment].update({"GITLAB_PRIVATE_TOKEN": "token"})
        mock_load_settings.assert_called_once()
        mock_write_settings.assert_called_once_with(ANY, data)


class TestSetupGitlabAddress:
    @patch("gl_search.clis.config._load_settings")
    @patch("gl_search.clis.config._write_settings")
    def test_call_methods(self, mock_write_settings: Mock, mock_load_settings: Mock) -> None:
        runner = CliRunner()
        result = runner.invoke(setup_gitlab_address, ["token"])
        assert result.exit_code == 0
        assert result.output == "Successfully registered.\n"
        mock_load_settings.assert_called_once()
        mock_write_settings.assert_called_once()

    @patch("gl_search.clis.config._load_settings")
    @patch("gl_search.clis.config._write_settings")
    def test_add_token(self, mock_write_settings: Mock, mock_load_settings: Mock) -> None:
        environment = "gl-settings"
        data = {environment: {}}
        mock_load_settings.return_value = deepcopy(data)
        runner = CliRunner()
        result = runner.invoke(setup_gitlab_address, ["token"])
        assert result.exit_code == 0
        assert result.output == "Successfully registered.\n"

        data[environment].update({"GITLAB_URL": "token"})
        mock_load_settings.assert_called_once()
        mock_write_settings.assert_called_once_with(ANY, data)
