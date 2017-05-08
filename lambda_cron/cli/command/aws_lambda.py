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

import os
import datetime
from command import AwsCommand


class InvokeCommand(AwsCommand):

    def payload(self):
        return "\"source\": \"LambdaCron-cli-invoke\", \"time\": \"{time}\", \"resources\": [\"Manual:invoke/LambdaCron-{environment}\"]".format(
            time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            environment=self.config.environment
        )

    def run(self):
        invoke_command = [
            "aws", "lambda", "invoke", "--invocation-type", "Event", "--function-name", self.get_stack_name(),
            "--payload", '{' + self.payload() + '}', os.path.join(self.get_tmp_directory(), 'invoke_output.txt')
        ]
        self.exec_command(invoke_command)
