# Copyright (C) 2016 MediaMath <http://www.mediamath.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from tests.utils import valid_cong_file_path
from lambda_cron.cli.cli_config import CliConfigParser
from lambda_cron.cli.command.cloudformation import CreateCommand
from argparse import Namespace


@pytest.fixture(scope='module')
def config_parser():
    return CliConfigParser(valid_cong_file_path())


class CreateCommandSpy(CreateCommand):

    def __init__(self, *kwargs):
        CreateCommand.__init__(self, *kwargs)
        self.commands_list = []
        self.lambda_function_config = {}

    def _exec(self, command):
        self.commands_list.append(command)

    def write_lambda_functions_config(self, config):
        self.lambda_function_config = config
        CreateCommand.write_lambda_functions_config(self, config)


def test_create_command_with_bucket_exists_not_create_bucket(monkeypatch, config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'create'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    cli_arguments.create_bucket = None
    create_command = CreateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    def bucket_exists():
        return True
    monkeypatch.setattr(create_command, 'bucket_exists', bucket_exists)

    create_command.run()

    assert len(create_command.commands_list) == 4
    assert 'pip' in create_command.commands_list[0]
    assert 's3' in create_command.commands_list[1] and 'cp' in create_command.commands_list[1]
    assert 's3://test-bucket-custom' in create_command.commands_list[1][4]
    assert '--profile' not in create_command.commands_list[1]
    assert 'create-stack' in create_command.commands_list[2]
    assert 'LambdaCron-prod' in create_command.commands_list[2]
    assert '--template-body' in create_command.commands_list[2]
    assert 'file://' in create_command.commands_list[2][6]
    assert '/lambda-cron/lambda_cron/template.cfn.yml' in create_command.commands_list[2][6]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-custom' in create_command.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=prod' in create_command.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in create_command.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in create_command.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in create_command.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=my@email.com' in create_command.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=300' in create_command.commands_list[2]
    assert '--profile' not in create_command.commands_list[2]
    assert 'stack-create-complete' in create_command.commands_list[3]
    assert '--profile' not in create_command.commands_list[3]


def test_create_command_with_bucket_not_exists_not_create_bucket(monkeypatch, config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'create'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    cli_arguments.create_bucket = None
    create_command = CreateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    def bucket_exists():
        return False
    monkeypatch.setattr(create_command, 'bucket_exists', bucket_exists)

    with pytest.raises(RuntimeError) as ex_info:
        create_command.run()

    assert "Bucket 'test-bucket-custom' does not exist" in str(ex_info)


def test_create_command_with_bucket_exists_create_bucket(monkeypatch, config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'create'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    cli_arguments.create_bucket = True
    create_command = CreateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    def bucket_exists():
        return True
    monkeypatch.setattr(create_command, 'bucket_exists', bucket_exists)

    with pytest.raises(RuntimeError) as ex_info:
        create_command.run()

    assert "Bucket 'test-bucket-custom' already exists" in str(ex_info)


def test_create_command_with_bucket_not_exists_create_bucket(monkeypatch, config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'create'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    cli_arguments.create_bucket = True
    create_command = CreateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    def bucket_exists():
        return False
    monkeypatch.setattr(create_command, 'bucket_exists', bucket_exists)

    create_command.run()

    assert len(create_command.commands_list) == 5
    assert set(['aws', 's3', 'mb']).issubset(create_command.commands_list[0])
    assert 'pip' in create_command.commands_list[1]
    assert 's3' in create_command.commands_list[2] and 'cp' in create_command.commands_list[2]
    assert 's3://test-bucket-custom' in create_command.commands_list[2][4]
    assert '--profile' not in create_command.commands_list[2]
    assert 'create-stack' in create_command.commands_list[3]
    assert 'LambdaCron-prod' in create_command.commands_list[3]
    assert '--template-body' in create_command.commands_list[3]
    assert 'file://' in create_command.commands_list[3][6]
    assert '/lambda-cron/lambda_cron/template.cfn.yml' in create_command.commands_list[3][6]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-custom' in create_command.commands_list[3]
    assert 'ParameterKey=Environment,ParameterValue=prod' in create_command.commands_list[3]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in create_command.commands_list[3]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in create_command.commands_list[3]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in create_command.commands_list[3]
    assert 'ParameterKey=AlarmEmail,ParameterValue=my@email.com' in create_command.commands_list[3]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=300' in create_command.commands_list[3]
    assert '--profile' not in create_command.commands_list[3]
    assert 'stack-create-complete' in create_command.commands_list[4]
    assert '--profile' not in create_command.commands_list[4]


def test_create_command_with_profile(monkeypatch, config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'create'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = 'test-profile'
    cli_arguments.create_bucket = True
    create_command = CreateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    def bucket_exists():
        return False
    monkeypatch.setattr(create_command, 'bucket_exists', bucket_exists)

    create_command.run()

    assert '--profile' in create_command.commands_list[0]
    assert 'test-profile' in create_command.commands_list[0]
    assert '--profile' in create_command.commands_list[2]
    assert 'test-profile' in create_command.commands_list[2]
    assert '--profile' in create_command.commands_list[3]
    assert 'test-profile' in create_command.commands_list[3]
    assert '--profile' in create_command.commands_list[4]
    assert 'test-profile' in create_command.commands_list[4]
