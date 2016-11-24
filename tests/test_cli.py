import cli.config_cli
from cli.lambda_cron_cli import LambdaCronCLI
import os
import pytest
from argparse import Namespace


def valid_cong_file_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/config.yml'))


def invalid_config_file_path():
    return '/tmp/no_existing_config.yml'


class LambdaCronCLISpy(LambdaCronCLI):
    def __init__(self, cli_instructions):
        LambdaCronCLI.__init__(self, cli_instructions)
        self.commands_list = []

    def exec_command(self, command):
        self.commands_list.append(command)


def test_create_command(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.state = 'DISABLED'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert 'pip' in lambda_cron.commands_list[0]
    assert 's3' in lambda_cron.commands_list[1] and 'cp' in lambda_cron.commands_list[1]
    assert 's3://test-bucket-custom' in lambda_cron.commands_list[1][4]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 'create-stack' in lambda_cron.commands_list[2]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-custom' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=prod' in lambda_cron.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=DISABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-create-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


def test_add_profile_to_aws_commands(monkeypatch):
    monkeypatch.setattr(cli.config_cli, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.state = 'DISABLED'
    cli_params.aws_profile = 'my-profile'

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert '--profile' in lambda_cron.commands_list[1]
    assert 'my-profile' in lambda_cron.commands_list[1]
    assert '--profile' in lambda_cron.commands_list[2]
    assert 'my-profile' in lambda_cron.commands_list[2]
    assert '--profile' in lambda_cron.commands_list[3]
    assert 'my-profile' in lambda_cron.commands_list[3]
