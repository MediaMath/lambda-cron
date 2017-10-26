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
from lambda_cron.cli.command.cloudformation import UpdateCommand
from argparse import Namespace


@pytest.fixture(scope='module')
def config_parser():
    return CliConfigParser(valid_cong_file_path())


class UpdateCommandSpy(UpdateCommand):

    def __init__(self, *kwargs):
        UpdateCommand.__init__(self, *kwargs)
        self.commands_list = []
        self.lambda_function_config = {}

    def _exec(self, command):
        self.commands_list.append(command)

    def write_lambda_functions_config(self, config):
        self.lambda_function_config = config
        UpdateCommand.write_lambda_functions_config(self, config)


def test_update_command(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'update'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    update_command = UpdateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    update_command.run()

    assert len(update_command.commands_list) == 4
    assert 'pip' in update_command.commands_list[0]
    assert '--profile' not in update_command.commands_list[0]
    assert 's3' in update_command.commands_list[1] and 'cp' in update_command.commands_list[1]
    assert 's3://test-bucket-custom' in update_command.commands_list[1][4]
    assert '--profile' not in update_command.commands_list[1]
    assert 'update-stack' in update_command.commands_list[2]
    assert 'LambdaCron-prod' in update_command.commands_list[2]
    assert '--template-body' in update_command.commands_list[2]
    assert 'file://' in update_command.commands_list[2][6]
    assert '/lambda-cron/lambda_cron/template.cfn.yml' in update_command.commands_list[2][6]
    assert 'ParameterKey=Bucket,ParameterValue=test-bucket-custom' in update_command.commands_list[2]
    assert 'ParameterKey=Environment,ParameterValue=prod' in update_command.commands_list[2]
    assert 'ParameterKey=State,ParameterValue=ENABLED' in update_command.commands_list[2]
    assert 'ParameterKey=CronExpression,ParameterValue=cron(*/5 * * * ? *)' in update_command.commands_list[2]
    assert 'ParameterKey=AlarmEnabled,ParameterValue=True' in update_command.commands_list[2]
    assert 'ParameterKey=AlarmEmail,ParameterValue=my@email.com' in update_command.commands_list[2]
    assert 'ParameterKey=AlarmPeriod,ParameterValue=300' in update_command.commands_list[2]
    assert '--profile' not in update_command.commands_list[2]
    assert 'stack-update-complete' in update_command.commands_list[3]
    assert '--profile' not in update_command.commands_list[3]


def test_update_command_with_profile(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'update'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = 'test-profile'
    update_command = UpdateCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    update_command.run()

    assert '--profile' not in update_command.commands_list[0]
    assert '--profile' in update_command.commands_list[1]
    assert 'test-profile' in update_command.commands_list[1]
    assert '--profile' in update_command.commands_list[2]
    assert 'test-profile' in update_command.commands_list[2]
    assert '--profile' in update_command.commands_list[3]
    assert 'test-profile' in update_command.commands_list[3]
