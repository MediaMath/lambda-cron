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

import argparse
import sys
from cli_config import CliConfigParser, get_default_cli_config_file_path
from command.cloudformation import *
from command.tasks import *
from command.aws_lambda import *


def check_arg(args=None):
    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(dest="command")

    deploy_command = commands_parser.add_parser('create')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')
    deploy_command.add_argument('--create-bucket', action='store_true', dest='create_bucket')

    deploy_command = commands_parser.add_parser('update')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')

    deploy_command = commands_parser.add_parser('start')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')

    deploy_command = commands_parser.add_parser('stop')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')

    deploy_command = commands_parser.add_parser('delete')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')
    deploy_command.add_argument('--delete-bucket', action='store_true', dest='delete_bucket')

    deploy_command = commands_parser.add_parser('invoke')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')

    deploy_command = commands_parser.add_parser('upload-tasks')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-d', '--directory', required=True)
    deploy_command.add_argument('-a', '--aws-profile', default=None, dest='aws_profile')

    deploy_command = commands_parser.add_parser('validate')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-t', '--task-file', required=False, dest='task_file')
    deploy_command.add_argument('-d', '--task-directory', required=False, dest='task_directory')

    return parser.parse_args(args)


class CliTool:

    def __init__(self, cli_instructions, config_file):
        self.cli = cli_instructions
        self.config = CliConfigParser(config_file).get_config(self.cli.environment)

    def print_summary(self):
        summary_line_format = "{:<15}: {:<15}"
        print summary_line_format.format('Environment', str(self.config.environment))
        print summary_line_format.format('Bucket', str(self.config.bucket))
        print summary_line_format.format('Enabled', str(self.config.enabled))
        print summary_line_format.format('Alarm enabled', str(self.config.alarm_enabled))
        print summary_line_format.format('Alarm email', self.config.alarm_email)
        print summary_line_format.format('Hours', str(self.config.hours))
        print summary_line_format.format('Minutes', str(self.config.minutes))

    def get_command_instance(self):
        command_class_name = "{}Command".format(self.cli.command.title())
        command_class_name = command_class_name.replace('-', '')
        command_class = globals()[command_class_name]
        return command_class(self.config, self.cli)

    def run(self):
        self.print_summary()
        command_instance = self.get_command_instance()
        try:
            command_instance.run()
        except Exception, ex:
            exit(1)
        exit(0)


def main():
    results = check_arg(sys.argv[1:])
    print results
    CliTool(results, get_default_cli_config_file_path()).run()
