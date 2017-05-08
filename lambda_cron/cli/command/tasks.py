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

import yaml
import jsonschema
import os
import json
from command import Command, AwsCommand, get_package_root_directory


def get_jsonschema_file_path():
    return os.path.join(get_package_root_directory(), 'schema.json')


def get_jsonschema():
    with open(get_jsonschema_file_path(), 'r') as schema_file:
        return json.load(schema_file)


class ValidateCommand(Command):

    @staticmethod
    def validate_task(schema, task_file_name):
        try:
            with open(task_file_name, 'r') as task_file:
                task = yaml.load(task_file)
            jsonschema.validate(task, schema)
        except Exception, ex:
            raise ex

    def run(self):
        if self.arguments.task_file and self.arguments.task_directory:
            raise RuntimeError('ValidateCommand, required only one of: task_file, task_directory')
        try:
            if self.arguments.task_file:
                self.validate_task(get_jsonschema(), self.arguments.task_file)

            if self.arguments.task_directory:
                all_yml_files = [os.path.join(dirpath, f)
                                 for dirpath, dirnames, files in os.walk(self.arguments.task_directory)
                                 for f in files]
                for file_name in all_yml_files:
                    if not file_name.endswith('.yml'):
                        raise RuntimeError('Task is not defined in YAML file (extension .yml): {}'.format(file_name))
                    self.validate_task(get_jsonschema(), file_name)
        except Exception, ex:
            print 'Error: {}'.format(str(ex))
            print 'Validation Failed!'
            raise ex

        print 'Validation Success!'


class UploadTasksCommand(AwsCommand):

    def run(self):
        upload_tasks_stack_command = [
            "aws", "s3", "sync", self.arguments.directory, "s3://{}/tasks/".format(self.config.bucket), '--delete'
        ]
        self.exec_command(upload_tasks_stack_command)
