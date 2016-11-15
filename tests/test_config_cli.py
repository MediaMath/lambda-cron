import cli.config_cli
import os


def valid_cong_file_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/config.yml'))


def invalid_config_file_path():
    return '/tmp/no_existing_config.yml'


def test_should_use_custom_bucket_for_environment(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    config = cli.config_cli.ConfigCli('prod')
    assert config.bucket == 'test-bucket-custom'


def test_should_use_bucket_for_all_environment(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    config = cli.config_cli.ConfigCli('other')
    assert config.bucket == 'test-bucket-all-other'


def test_should_use_default_bucket(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', invalid_config_file_path)
    config = cli.config_cli.ConfigCli('test')
    assert config.bucket == 'LambdaCron-test'


