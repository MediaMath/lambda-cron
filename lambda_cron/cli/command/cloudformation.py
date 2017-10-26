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
import yaml
import shutil
from zipfile import ZipFile
from command import AwsCommand, get_package_root_directory

def get_cloudformation_template():
    return os.path.join(get_package_root_directory(), 'template.cfn.yml')


def get_aws_directory():
    return os.path.abspath(os.path.join(get_package_root_directory(), 'aws'))


def get_cron_unit_expression(value):
    if value == 1:
        return '*'
    else:
        return "*/{}".format(value)


def get_requirements_txt():
    return os.path.join(get_package_root_directory(), 'requirements.txt')


def zip_dir(zip_file, path, prefix=''):
    for root, dirs, files in os.walk(path):
        for file in files:
            absolute_path = os.path.join(root, file)
            relative_path = absolute_path[len(path) + len(os.sep):]
            if prefix:
                relative_path = os.path.join(prefix, relative_path)
            zip_file.write(absolute_path, relative_path)


class CloudFormationCommand(AwsCommand):

    def run(self):
        raise NotImplementedError

    def is_template_required(self):
        raise NotImplementedError

    def get_parameter_value(self, value):
        return "ParameterValue={}".format(value)

    def get_state_value(self):
        if self.config.enabled:
            return 'ENABLED'
        else:
            return 'DISABLED'

    def get_code_key_parameter(self):
        return "ParameterValue=code/{}".format(self.get_code_zip_file_name())

    def add_template_parameters(self, command):
        command.append("--parameters")
        command.append("ParameterKey=Environment,ParameterValue={environment}".format(environment=self.config.environment))
        command.append("ParameterKey=State,ParameterValue={state}".format(state=self.get_state_value())),
        command.append("ParameterKey=CodeS3Key,{}".format(self.get_code_key_parameter()))
        command.append("ParameterKey=Bucket,{}".format(self.get_parameter_value(self.config.bucket)))
        command.append("ParameterKey=CronExpression,{}".format(self.get_parameter_value(self.get_cron_expression())))
        command.append("ParameterKey=AlarmEnabled,{}".format(self.get_parameter_value(self.config.alarm_enabled)))
        if self.config.alarm_enabled:
            command.append("ParameterKey=AlarmEmail,{}".format(self.get_parameter_value(self.config.alarm_email)))
            command.append("ParameterKey=AlarmPeriod,{}".format(self.get_parameter_value(self.get_alarm_period())))
        return command

    def upload_code_to_s3(self):
        s3_target_path = "s3://{bucket}/code/{file}".format(bucket=self.config.bucket,
                                                            file=self.get_code_zip_file_name())
        s3_upload_command = ["aws", "s3", "cp", self.get_code_zip_file_path(), s3_target_path]
        self.exec_command(s3_upload_command)

    def run_cloudformation_wait_command(self, action):
        wait_create_stack_command = [
            "aws", "cloudformation", "wait", "stack-{}-complete".format(action),
            "--stack-name", self.get_stack_name()
        ]
        self.exec_command(wait_create_stack_command)

    def add_template_to_command(self, cf_command):
        cf_command.append("--template-body")
        cf_command.append("file://{}".format(get_cloudformation_template()))
        cf_command.append("--capabilities")
        cf_command.append("CAPABILITY_NAMED_IAM")
        return self.add_template_parameters(cf_command)

    def get_cron_expression(self):
        minutes = hours = '*'
        if self.config.minutes:
            hours = '*'
            minutes = get_cron_unit_expression(self.config.minutes)
        elif self.config.hours:
            minutes = '0'
            hours = get_cron_unit_expression(self.config.hours)
        return "cron({minutes} {hours} * * ? *)".format(minutes=minutes, hours=hours)

    def get_alarm_period(self):
        if self.config.minutes:
            return self.config.minutes * 60
        return self.config.hours * 3600

    def run_cloudformation_command(self, action):
        cf_command = [
            "aws", "cloudformation", "{}-stack".format(action), "--stack-name", self.get_stack_name(),
        ]
        if self.is_template_required():
            cf_command = self.add_template_to_command(cf_command)
        self.exec_command(cf_command)
        self.run_cloudformation_wait_command(action)

    def zip_lambda_function_dependencies(self, zip_file, tmp_directory):
        dependencies_directory = os.path.join(tmp_directory, 'dependencies')
        os.mkdir(dependencies_directory)
        pip_install_command = ["pip", "install", "--requirement",
                               get_requirements_txt(),
                               "--target", dependencies_directory,
                               "--ignore-installed"]
        self.exec_command(pip_install_command, use_profile=False)
        zip_dir(zip_file, dependencies_directory)

    def generate_lambda_functions_config(self, config_file_path):
        lambda_function_config = {
            'bucket': self.config.bucket,
            'frequency': {
                'hours': self.config.hours,
                'minutes': self.config.minutes
            }
        }
        with open(config_file_path, 'w') as outfile:
            yaml.dump(lambda_function_config, outfile, default_flow_style=False)

    def zip_lambda_function_config(self, zip_file, tmp_directory):
        config_file_path = os.path.abspath(os.path.join(tmp_directory, 'config.yml'))
        self.generate_lambda_functions_config(config_file_path)
        zip_file.write(config_file_path, 'config.yml')

    def get_code_zip_file_name(self):
        return "code_{}.zip".format(self.timestamp)

    def get_code_zip_file_path(self):
        return os.path.abspath(os.path.join(self.get_tmp_directory(), self.get_code_zip_file_name()))

    def zip_code(self):
        tmp_directory = self.get_tmp_directory()
        if os.path.exists(tmp_directory):
            shutil.rmtree(tmp_directory)
        os.mkdir(tmp_directory)
        with ZipFile(self.get_code_zip_file_path(), 'w') as zip_file:
            self.zip_lambda_function_dependencies(zip_file, tmp_directory)
            self.zip_lambda_function_config(zip_file, tmp_directory)
            zip_dir(zip_file, os.path.join(get_aws_directory(), 'lib'), 'lib')
            zip_file.write(os.path.join(get_aws_directory(), 'main.py'), 'main.py')


class CreateCommand(CloudFormationCommand):

    def bucket_exists(self):
        check_bucket_command = ["aws", "s3api", "head-bucket", "--bucket", self.config.bucket]
        command_result = self.exec_command(check_bucket_command)
        return command_result == 0

    def check_bucket(self):
        bucket_exists = self.bucket_exists()
        try:
            if self.arguments.create_bucket:
                if not bucket_exists:
                    print "Creating bucket '{}'".format(self.config.bucket)
                    create_bucket_command = ["aws", "s3", "mb", self.get_s3_bucket_uri()]
                    self.exec_command(create_bucket_command)
                else:
                    raise RuntimeError("Bucket '{}' already exists".format(self.config.bucket))
            else:
                if not bucket_exists:
                    raise RuntimeError("Bucket '{}' does not exist".format(self.config.bucket))
        except RuntimeError, ex:
            print ex.message
            raise ex

    def is_template_required(self):
        return True

    def create_stack(self):
        self.run_cloudformation_command('create')

    def run(self):
        self.check_bucket()
        self.zip_code()
        self.upload_code_to_s3()
        self.create_stack()


class UpdateCommand(CloudFormationCommand):

    def is_template_required(self):
        return True

    def update_stack(self):
        self.run_cloudformation_command('update')

    def run(self):
        self.zip_code()
        self.upload_code_to_s3()
        self.update_stack()


class DeleteCommand(CloudFormationCommand):

    def is_template_required(self):
        return False

    def run(self):
        self.run_cloudformation_command('delete')

        if self.arguments.delete_bucket:
            delete_bucket_command = ["aws", "s3", "rb", self.get_s3_bucket_uri()]
            self.exec_command(delete_bucket_command)


class StartCommand(CloudFormationCommand):

    def is_template_required(self):
        return True

    def run(self):
        self.run_cloudformation_command('update')

    def get_state_value(self):
        return 'ENABLED'

    def get_parameter_value(self, value):
        return "UsePreviousValue=true"

    def get_code_key_parameter(self):
        return "UsePreviousValue=true"


class StopCommand(CloudFormationCommand):

    def is_template_required(self):
        return True

    def run(self):
        self.run_cloudformation_command('update')

    def get_state_value(self):
        return 'DISABLED'

    def get_parameter_value(self, value):
        return "UsePreviousValue=true"

    def get_code_key_parameter(self):
        return "UsePreviousValue=true"
