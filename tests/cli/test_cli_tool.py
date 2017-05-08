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
from argparse import Namespace
from tests.utils import valid_cong_file_path
from lambda_cron.cli.cli_tool import CliTool
from lambda_cron.cli.command.cloudformation import *
from lambda_cron.cli.command.tasks import *
from lambda_cron.cli.command.aws_lambda import *


def test_cli_create_command():
    cli_params = Namespace()
    cli_params.command = 'create'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), CreateCommand)


def test_cli_update_command():
    cli_params = Namespace()
    cli_params.command = 'update'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), UpdateCommand)


def test_cli_delete_command():
    cli_params = Namespace()
    cli_params.command = 'delete'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), DeleteCommand)


def test_cli_start_command():
    cli_params = Namespace()
    cli_params.command = 'start'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), StartCommand)


def test_cli_stop_command(monkeypatch):
    cli_params = Namespace()
    cli_params.command = 'stop'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), StopCommand)


def test_cli_validate_command():
    cli_params = Namespace()
    cli_params.command = 'validate'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), ValidateCommand)


def test_cli_upload_tasks_command():
    cli_params = Namespace()
    cli_params.command = 'upload-tasks'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), UploadTasksCommand)


def test_cli_inovke_command():
    cli_params = Namespace()
    cli_params.command = 'invoke'
    cli_params.environment = 'prod'

    assert isinstance(CliTool(cli_params, valid_cong_file_path()).get_command_instance(), InvokeCommand)
