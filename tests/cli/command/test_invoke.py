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
from lambda_cron.cli.command.aws_lambda import InvokeCommand
from argparse import Namespace


@pytest.fixture(scope='module')
def config_parser():
    return CliConfigParser(valid_cong_file_path())


class InvokeCommandSpy(InvokeCommand):

    def __init__(self, *kwargs):
        InvokeCommand.__init__(self, *kwargs)
        self.commands_list = []
        self.lambda_function_config = {}

    def _exec(self, command):
        self.commands_list.append(command)


def test_invoke_command(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'invoke'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = None
    invoke_command = InvokeCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    invoke_command.run()

    assert len(invoke_command.commands_list) == 1
    assert 'lambda' in invoke_command.commands_list[0]
    assert 'invoke' in invoke_command.commands_list[0]
    assert 'LambdaCron-prod' in invoke_command.commands_list[0]
    assert '--payload' in invoke_command.commands_list[0]
    assert '--profile' not in invoke_command.commands_list[0]


def test_invoke_command_with_profile(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'invoke'
    cli_arguments.environment = 'prod'
    cli_arguments.aws_profile = 'test-profile'
    invoke_command = InvokeCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    invoke_command.run()

    assert len(invoke_command.commands_list) == 1
    assert '--profile' in invoke_command.commands_list[0]
    assert 'test-profile' in invoke_command.commands_list[0]
