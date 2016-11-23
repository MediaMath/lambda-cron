import cli.config_cli
import os
import pytest


def valid_cong_file_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/config.yml'))


def invalid_config_file_path():
    return '/tmp/no_existing_config.yml'


def test_should_use_custom_for_environment(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    config = cli.config_cli.ConfigCli('prod')
    assert config.bucket == 'test-bucket-custom'
    assert config.alarm


def test_should_use_for_all_environment(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    config = cli.config_cli.ConfigCli('other')
    assert config.bucket == 'test-bucket-all-other'
    assert config.alarm == False


def test_should_use_for_all_environment_2(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    config = cli.config_cli.ConfigCli('staging')
    assert config.bucket == 'test-bucket-all-staging'
    assert config.alarm == False


def test_should_use_global_default_settings(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', invalid_config_file_path)
    config = cli.config_cli.ConfigCli('test')
    assert config.bucket == 'LambdaCron-test'
    assert config.alarm == False


def test_alarm_should_be_false_for_invalid_values(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', invalid_config_file_path)
    config = cli.config_cli.ConfigCli('bad_alarm')
    assert config.alarm == False
