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
from tests.utils import *
from lambda_cron.cli.cli_config import CliConfig
from lambda_cron.cli.command.tasks import ValidateCommand
from jsonschema.exceptions import ValidationError
from argparse import Namespace


def test_validate_command_queue_task():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('valid/queue_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_command_http_get_task():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('valid/http_get_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_command_http_post_task():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('valid/http_post_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_command_lambda_task():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('valid/lambda_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_command_athena_task():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('valid/athena_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_command_with_error():
    cli_arguments = Namespace()
    cli_arguments.task_file = get_test_task_path('invalid/invalid_task.yml')
    cli_arguments.task_directory = None
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)

    with pytest.raises(ValidationError) as ex_info:
        validate_command.run()

    assert "ValidationError: '0 a * * *' does not match" in str(ex_info)


def test_validate_command_directory():
    cli_arguments = Namespace()
    cli_arguments.task_file = None
    cli_arguments.task_directory = os.path.join(resources_directory_path(), 'tasks', 'valid')
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)
    validate_command.run()


def test_validate_invalid_file_extension():
    cli_arguments = Namespace()
    cli_arguments.task_file = None
    cli_arguments.task_directory = os.path.join(resources_directory_path(), 'tasks')
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)

    with pytest.raises(RuntimeError) as ex_info:
        validate_command.run()

    assert "Task is not defined in YAML file (extension .yml):" in str(ex_info)


def test_validate_only_test_file_or_directory():
    cli_arguments = Namespace()
    cli_arguments.task_file = 'my-files/task.yml'
    cli_arguments.task_directory = 'my-files/'
    validate_command = ValidateCommand(CliConfig('test'), cli_arguments)

    with pytest.raises(RuntimeError) as ex_info:
        validate_command.run()

    assert "ValidateCommand, required only one of: task_file, task_directory" in str(ex_info)
