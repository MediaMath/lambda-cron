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
from lambda_cron.cli.command.cloudformation import DeleteCommand
from argparse import Namespace


@pytest.fixture(scope='module')
def config_parser():
    return CliConfigParser(valid_cong_file_path())


class DeleteCommandSpy(DeleteCommand):

    def __init__(self, *kwargs):
        DeleteCommand.__init__(self, *kwargs)
        self.commands_list = []
        self.lambda_function_config = {}

    def _exec(self, command):
        self.commands_list.append(command)


def test_delete_command(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'delete'
    cli_arguments.environment = 'prod'
    cli_arguments.delete_bucket = None
    cli_arguments.aws_profile = None
    delete_command = DeleteCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    delete_command.run()

    assert len(delete_command.commands_list) == 2
    assert 'delete-stack' in delete_command.commands_list[0]
    assert 'LambdaCron-prod' in delete_command.commands_list[0]
    assert '--profile' not in delete_command.commands_list[0]
    assert 'stack-delete-complete' in delete_command.commands_list[1]
    assert '--profile' not in delete_command.commands_list[1]


def test_delete_command_with_delete_bucket(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'delete'
    cli_arguments.environment = 'prod'
    cli_arguments.delete_bucket = True
    cli_arguments.aws_profile = None
    delete_command = DeleteCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    delete_command.run()

    assert len(delete_command.commands_list) == 3
    assert 'delete-stack' in delete_command.commands_list[0]
    assert 'LambdaCron-prod' in delete_command.commands_list[0]
    assert '--profile' not in delete_command.commands_list[0]
    assert 'stack-delete-complete' in delete_command.commands_list[1]
    assert '--profile' not in delete_command.commands_list[1]
    assert 's3' in delete_command.commands_list[2]
    assert 'rb' in delete_command.commands_list[2]
    assert 's3://test-bucket-custom' in delete_command.commands_list[2]
    assert '--profile' not in delete_command.commands_list[2]


def test_delete_command_with_delete_bucket_and_profile(config_parser):
    cli_arguments = Namespace()
    cli_arguments.command = 'delete'
    cli_arguments.environment = 'prod'
    cli_arguments.delete_bucket = True
    cli_arguments.aws_profile = 'test-profile'
    delete_command = DeleteCommandSpy(config_parser.get_config(cli_arguments.environment), cli_arguments)

    delete_command.run()

    assert len(delete_command.commands_list) == 3
    assert '--profile' in delete_command.commands_list[0]
    assert 'test-profile' in delete_command.commands_list[0]
    assert '--profile' in delete_command.commands_list[1]
    assert 'test-profile' in delete_command.commands_list[0]
    assert '--profile' in delete_command.commands_list[2]
    assert 'test-profile' in delete_command.commands_list[0]
