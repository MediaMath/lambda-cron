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

import lambda_cron.cli.cli_config as cli_config
from lambda_cron.cli.cli_tool import CliTool as LambdaCronCLI
import os
import pytest
from mock import patch
from argparse import Namespace


def resources_directory_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources'))


def valid_cong_file_path():
    return os.path.join(resources_directory_path(), 'config.yml')


def invalid_config_file_path():
    return '/tmp/no_existing_config.yml'


def get_test_task_path(task_file_name):
    return os.path.join(resources_directory_path(), 'tasks', task_file_name)


class LambdaCronCLISpy(LambdaCronCLI):
    def __init__(self, cli_instructions):
        LambdaCronCLI.__init__(self, cli_instructions)
        self.commands_list = []
        self.lambda_function_config = {}

    def exec_command(self, command):
        self.commands_list.append(command)

    def write_lambda_functions_config(self, config):
        self.lambda_function_config = config
        LambdaCronCLI.write_lambda_functions_config(self, config)


@patch.object(LambdaCronCLISpy, 'check_bucket')
def test_create_command(check_bucket_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
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
    assert 'ParameterKey=State,ParameterValue=ENABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=my@email.com' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=300' in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-create-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


@patch.object(LambdaCronCLISpy, 'check_bucket')
def test_add_profile_to_create_commands(check_bucket_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
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


def test_update_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'prod'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert 'pip' in lambda_cron.commands_list[0]
    assert 's3' in lambda_cron.commands_list[1] and 'cp' in lambda_cron.commands_list[1]
    assert 's3://test-bucket-custom' in lambda_cron.commands_list[1][4]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 'update-stack' in lambda_cron.commands_list[2]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-custom' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=prod' in lambda_cron.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=my@email.com' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=300' in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-update-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


def test_add_profile_to_update_commands(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'prod'
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


def test_delete_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'delete'
    cli_params.environment = 'prod'
    cli_params.delete_bucket = False
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert 'delete-stack' in lambda_cron.commands_list[0]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[0]
    assert '--profile' not in lambda_cron.commands_list[0]
    assert 'stack-delete-complete' in lambda_cron.commands_list[1]
    assert '--profile' not in lambda_cron.commands_list[1]


def test_delete_command_with_delete_bucket(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'delete'
    cli_params.environment = 'prod'
    cli_params.delete_bucket = True
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 3
    assert 'delete-stack' in lambda_cron.commands_list[0]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[0]
    assert '--profile' not in lambda_cron.commands_list[0]
    assert 'stack-delete-complete' in lambda_cron.commands_list[1]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 's3' in lambda_cron.commands_list[2]
    assert 'rb' in lambda_cron.commands_list[2]
    assert 's3://test-bucket-custom' in lambda_cron.commands_list[2]


def test_add_profile_to_delete_commands(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'delete'
    cli_params.environment = 'prod'
    cli_params.delete_bucket = False
    cli_params.aws_profile = 'my-profile'

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert '--profile' in lambda_cron.commands_list[0]
    assert 'my-profile' in lambda_cron.commands_list[0]
    assert '--profile' in lambda_cron.commands_list[1]
    assert 'my-profile' in lambda_cron.commands_list[1]


def test_invoke_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'invoke'
    cli_params.environment = 'prod'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 1
    assert 'lambda' in lambda_cron.commands_list[0]
    assert 'invoke' in lambda_cron.commands_list[0]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[0]
    assert '--profile' not in lambda_cron.commands_list[0]


def test_add_profile_to_invoke_commands(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'invoke'
    cli_params.environment = 'prod'
    cli_params.aws_profile = 'my-profile'

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 1
    assert '--profile' in lambda_cron.commands_list[0]
    assert 'my-profile' in lambda_cron.commands_list[0]


@patch.object(LambdaCronCLISpy, 'check_bucket')
def test_lambda_function_config(check_bucket_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    expected_config = {
        'bucket': 'test-bucket-custom',
        'frequency': {
            'minutes': 5,
            'hours': 0
        }
    }

    assert lambda_cron.lambda_function_config == expected_config


@patch.object(LambdaCronCLISpy, 'check_bucket')
def test_lambda_function_config_II(check_bucket_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'other'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    expected_config = {
        'bucket': 'test-bucket-all-other',
        'frequency': {
            'hours': 2,
            'minutes': 0
        }
    }

    assert lambda_cron.lambda_function_config == expected_config


def test_update_command_other_env(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'other'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert 'pip' in lambda_cron.commands_list[0]
    assert 's3' in lambda_cron.commands_list[1] and 'cp' in lambda_cron.commands_list[1]
    assert 's3://test-bucket-all-other' in lambda_cron.commands_list[1][4]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 'update-stack' in lambda_cron.commands_list[2]
    assert 'LambdaCron-other' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-all-other' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=other' in lambda_cron.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(0 */2 * * ? *)' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=False' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=' not in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=' not in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-update-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


def test_update_command_test_env(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'test'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert 'pip' in lambda_cron.commands_list[0]
    assert 's3' in lambda_cron.commands_list[1] and 'cp' in lambda_cron.commands_list[1]
    assert 's3://test-bucket-all-test' in lambda_cron.commands_list[1][4]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 'update-stack' in lambda_cron.commands_list[2]
    assert 'LambdaCron-test' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-all-test' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=test' in lambda_cron.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(* * * * ? *)' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=test@email.com' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=60' in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-update-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


def test_update_command_develop_env(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'develop'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 4
    assert 'pip' in lambda_cron.commands_list[0]
    assert 's3' in lambda_cron.commands_list[1] and 'cp' in lambda_cron.commands_list[1]
    assert 's3://test-bucket-all-develop' in lambda_cron.commands_list[1][4]
    assert '--profile' not in lambda_cron.commands_list[1]
    assert 'update-stack' in lambda_cron.commands_list[2]
    assert 'LambdaCron-develop' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-all-develop' in lambda_cron.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=develop' in lambda_cron.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=DISABLED' in lambda_cron.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(0 * * * ? *)' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=develop@email.com' in lambda_cron.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=3600' in lambda_cron.commands_list[2]
    assert '--profile' not in lambda_cron.commands_list[2]
    assert 'stack-update-complete' in lambda_cron.commands_list[3]
    assert '--profile' not in lambda_cron.commands_list[3]


def test_start_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'start'
    cli_params.environment = 'prod'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert 'update-stack' in lambda_cron.commands_list[0]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[0]
    assert 'ParameterKey=CodeS3Key,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=Bucket,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=Environment,ParameterValue=prod' in lambda_cron.commands_list[0]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in lambda_cron.commands_list[0]
    assert 'ParameterKey=CronExpression,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmEnabled,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmEmail,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmPeriod,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert '--profile' not in lambda_cron.commands_list[0]
    assert 'stack-update-complete' in lambda_cron.commands_list[1]
    assert '--profile' not in lambda_cron.commands_list[1]


def test_add_profile_to_start_commands(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'start'
    cli_params.environment = 'prod'
    cli_params.aws_profile = 'my-profile'

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert '--profile' in lambda_cron.commands_list[0]
    assert 'my-profile' in lambda_cron.commands_list[0]
    assert '--profile' in lambda_cron.commands_list[1]
    assert 'my-profile' in lambda_cron.commands_list[1]


def test_stop_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'stop'
    cli_params.environment = 'prod'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert 'update-stack' in lambda_cron.commands_list[0]
    assert 'LambdaCron-prod' in lambda_cron.commands_list[0]
    assert 'ParameterKey=CodeS3Key,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=Bucket,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=Environment,ParameterValue=prod' in lambda_cron.commands_list[0]
    assert 'ParameterKey=State,ParameterValue=DISABLED' in lambda_cron.commands_list[0]
    assert 'ParameterKey=CronExpression,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmEnabled,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmEmail,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert 'ParameterKey=AlarmPeriod,UsePreviousValue=true' in lambda_cron.commands_list[0]
    assert '--profile' not in lambda_cron.commands_list[0]
    assert 'stack-update-complete' in lambda_cron.commands_list[1]
    assert '--profile' not in lambda_cron.commands_list[1]


def test_add_profile_to_stop_commands(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'stop'
    cli_params.environment = 'prod'
    cli_params.aws_profile = 'my-profile'

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 2
    assert '--profile' in lambda_cron.commands_list[0]
    assert 'my-profile' in lambda_cron.commands_list[0]
    assert '--profile' in lambda_cron.commands_list[1]
    assert 'my-profile' in lambda_cron.commands_list[1]


@patch.object(LambdaCronCLISpy, 'bucket_exists')
def test_check_bucket_need_create_bucket(bucket_exists_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    bucket_exists_mock.return_value = False
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.create_bucket = True
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.check_bucket()

    assert len(lambda_cron.commands_list) == 1
    assert "aws" in lambda_cron.commands_list[0]
    assert "s3" in lambda_cron.commands_list[0]
    assert "mb" in lambda_cron.commands_list[0]
    assert "s3://test-bucket-custom" in lambda_cron.commands_list[0]


@patch.object(LambdaCronCLISpy, 'bucket_exists')
def test_check_bucket_bucket_already_exists_error(bucket_exists_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    bucket_exists_mock.return_value = True
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.create_bucket = True
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    with pytest.raises(SystemExit) as system_exit:
        lambda_cron.check_bucket()

    assert system_exit.value.code == 1


@patch.object(LambdaCronCLISpy, 'bucket_exists')
def test_check_bucket_bucket_already_exists_ok(bucket_exists_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    bucket_exists_mock.return_value = True
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.create_bucket = False
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.check_bucket()

    assert len(lambda_cron.commands_list) == 0


@patch.object(LambdaCronCLISpy, 'bucket_exists')
def test_check_bucket_bucket_does_not_exist_error(bucket_exists_mock, monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    bucket_exists_mock.return_value = False
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'
    cli_params.create_bucket = False
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    with pytest.raises(SystemExit) as system_exit:
        lambda_cron.check_bucket()

    assert system_exit.value.code == 2


def test_upload_tasks_command(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'upload-tasks'
    cli_params.environment = 'prod'
    cli_params.directory = '/path/to/source/directory'
    cli_params.aws_profile = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()

    assert len(lambda_cron.commands_list) == 1
    assert 's3' in lambda_cron.commands_list[0]
    assert 'sync' in lambda_cron.commands_list[0]
    assert '/path/to/source/directory' in lambda_cron.commands_list[0]
    assert 's3://test-bucket-custom/tasks/' in lambda_cron.commands_list[0]
    assert '--delete' in lambda_cron.commands_list[0]


def test_validate_command_queue_task(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = get_test_task_path('valid/queue_task.yml')
    cli_params.task_directory = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()


def test_validate_command_http_get_task(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = get_test_task_path('valid/http_get_task.yml')
    cli_params.task_directory = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()


def test_validate_command_http_post_task(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = get_test_task_path('valid/http_post_task.yml')
    cli_params.task_directory = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()


def test_validate_command_lambda_task(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = get_test_task_path('valid/lambda_task.yml')
    cli_params.task_directory = None

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()


def test_validate_command_with_error(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = get_test_task_path('invalid/invalid_task.yml')
    cli_params.task_directory = None

    lambda_cron = LambdaCronCLISpy(cli_params)

    with pytest.raises(SystemExit) as system_exit:
        lambda_cron.run()

    assert system_exit.value.code == 1


def test_validate_command_directory(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = None
    cli_params.task_directory = os.path.join(resources_directory_path(), 'tasks', 'valid')

    lambda_cron = LambdaCronCLISpy(cli_params)
    lambda_cron.run()


def test_validate_command_directory_error(monkeypatch):
    monkeypatch.setattr(cli_config, 'get_cli_config_file_path', valid_cong_file_path)
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.task_file = None
    cli_params.task_directory = os.path.join(resources_directory_path(), 'tasks')

    lambda_cron = LambdaCronCLISpy(cli_params)

    with pytest.raises(SystemExit) as system_exit:
        lambda_cron.run()

    assert system_exit.value.code == 1
