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
from lambda_cron.cli.command.cloudformation import StopCommand
from argparse import Namespace


@pytest.fixture(scope='module')
def config_parser():
    return CliConfigParser(valid_cong_file_path())


class StopCommandSpy(StopCommand):

    def __init__(self, *kwargs):
        StopCommand.__init__(self, *kwargs)
        self.commands_list = []
        self.lambda_function_config = {}

    def _exec(self, command):
        self.commands_list.append(command)


def test_start_command(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'stop'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    stop_command = StopCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    stop_command.run()

    assert len(stop_command.commands_list) == 2
    assert 'update-stack' in stop_command.commands_list[0]
    assert 'LambdaCron-prod' in stop_command.commands_list[0]
    assert '--template-body' in stop_command.commands_list[0]
    assert 'file://' in stop_command.commands_list[0][6]
    assert '/lambda-cron/lambda_cron/template.cfn.yml' in stop_command.commands_list[0][6]
    assert 'ParameterKey=CodeS3Key,UsePreviousValue=true' in stop_command.commands_list[0]
    assert 'ParameterKey=Bucket,UsePreviousValue=true' in stop_command.commands_list[0]
    assert 'ParameterKey=Environment,ParameterValue=prod' in stop_command.commands_list[0]
    assert 'ParameterKey=State,ParameterValue=DISABLED' in stop_command.commands_list[0]
    assert 'ParameterKey=CronExpression,UsePreviousValue=true' in stop_command.commands_list[0]
    assert 'ParameterKey=AlarmEnabled,UsePreviousValue=true' in stop_command.commands_list[0]
    assert 'ParameterKey=AlarmEmail,UsePreviousValue=true' in stop_command.commands_list[0]
    assert 'ParameterKey=AlarmPeriod,UsePreviousValue=true' in stop_command.commands_list[0]
    assert '--profile' not in stop_command.commands_list[0]
    assert 'stack-update-complete' in stop_command.commands_list[1]
    assert '--profile' not in stop_command.commands_list[1]


def test_start_command_with_profile(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'stop'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = 'test-profile'
    stop_command = StopCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    stop_command.run()

    assert len(stop_command.commands_list) == 2
    assert '--profile' in stop_command.commands_list[0]
    assert 'test-profile' in stop_command.commands_list[0]
    assert '--profile' in stop_command.commands_list[1]
    assert 'test-profile' in stop_command.commands_list[1]
