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

import time
import os
import subprocess


def get_package_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))


class Command:

    def __init__(self, cli_config, cli_arguments):
        self.config = cli_config
        self.arguments = cli_arguments
        self.timestamp = int(round(time.time() * 1000))

    def run(self):
        raise NotImplementedError()

    def exec_command(self, command):
        return self._exec(command)

    def _exec(self, command):
        return subprocess.call(command)

    def get_tmp_directory(self):
        return '/tmp/LambdaCron-{environment}'.format(environment=self.arguments.environment)


class AwsCommand(Command):

    def run(self):
        raise NotImplementedError

    def exec_command(self, command):
        if self.arguments.aws_profile:
            command.append('--profile')
            command.append(self.arguments.aws_profile)
        return Command.exec_command(self, command)

    def get_stack_name(self):
        return "LambdaCron-{environment}".format(environment=self.arguments.environment)

    def get_s3_bucket_uri(self):
        return "s3://{bucket_name}".format(bucket_name=self.config.bucket)
