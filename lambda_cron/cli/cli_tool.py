import argparse
import sys
import subprocess
import shutil
import os
import time
import datetime
from zipfile import ZipFile
from cli_config import CliConfig
import cli_config
import yaml
import json
import jsonschema


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
    deploy_command.add_argument('-t', '--task-file', required=False, dest='task_file')
    deploy_command.add_argument('-d', '--task-directory', required=False, dest='task_directory')

    return parser.parse_args(args)


def get_aws_directory():
    return os.path.abspath(os.path.join(cli_config.get_package_root_directory(), 'aws'))


def get_lambda_cron_path(sub_path):
    return os.path.join(get_aws_directory(), sub_path)


def zip_dir(zip_file, path, prefix=''):
    for root, dirs, files in os.walk(path):
        for file in files:
            absolute_path = os.path.join(root, file)
            relative_path = absolute_path[len(path) + len(os.sep):]
            if prefix:
                relative_path = os.path.join(prefix, relative_path)
            zip_file.write(absolute_path, relative_path)


class CliTool:

    def __init__(self, cli_instructions):
        self.cli = cli_instructions
        self.timestamp = int(round(time.time() * 1000))
        if self.is_config_required():
            self.config = CliConfig(self.cli.environment)

    def is_config_required(self):
        return 'environment' in self.cli

    def get_tmp_directory(self):
        return '/tmp/LambdaCron-{environment}'.format(environment=self.cli.environment)

    def get_dependencies_directory(self):
        return os.path.join(self.get_tmp_directory(), 'dependencies')

    def get_code_zip_file_name(self):
        return "code_{}.zip".format(self.timestamp)

    def get_code_zip_file_path(self):
        return os.path.abspath(os.path.join(self.get_tmp_directory(), self.get_code_zip_file_name()))

    def get_config_file_path(self):
        return os.path.abspath(os.path.join(self.get_tmp_directory(), 'config.yml'))

    def get_stack_name(self):
        return "LambdaCron-{environment}".format(environment=self.cli.environment)

    def install_dependencies(self):
        pip_install_command = ["pip", "install", "--requirement",
                               os.path.join(cli_config.get_package_root_directory(), 'requirements.txt'),
                               "--target", self.get_dependencies_directory(),
                               "--ignore-installed"]
        os.mkdir(self.get_dependencies_directory())
        self.exec_command(pip_install_command)

    def exec_command(self, command):
        return subprocess.call(command)

    def exec_aws_command(self, command):
        if self.cli.aws_profile:
            command.append('--profile')
            command.append(self.cli.aws_profile)
        return self.exec_command(command)

    def generate_config(self):
        lambda_function_config = {
            'bucket': self.config.bucket,
            'frequency': {
                'hours': self.config.hours,
                'minutes': self.config.minutes
            }
        }
        self.write_lambda_functions_config(lambda_function_config)

    def write_lambda_functions_config(self, config):
        with open(self.get_config_file_path(), 'w') as outfile:
            yaml.dump(config, outfile, default_flow_style=False)

    def zip_code(self):
        tmp_directory = self.get_tmp_directory()
        if os.path.exists(tmp_directory):
            shutil.rmtree(tmp_directory)
        os.mkdir(tmp_directory)
        self.install_dependencies()
        self.generate_config()
        with ZipFile(self.get_code_zip_file_path(), 'w') as zip_file:
            zip_dir(zip_file, self.get_dependencies_directory())
            zip_dir(zip_file, os.path.join(get_aws_directory(), 'lib'), 'lib')
            zip_file.write(os.path.join(get_aws_directory(), 'main.py'), 'main.py')
            zip_file.write(self.get_config_file_path(), 'config.yml')

    def get_cron_expression(self):
        if self.config.minutes:
            if self.config.minutes == 1:
                return 'cron(* * * * ? *)'
            else:
                return "cron(*/{} * * * ? *)".format(self.config.minutes)
        elif self.config.hours:
            if self.config.hours == 1:
                return 'cron(0 * * * ? *)'
            else:
                return "cron(0 */{} * * ? *)".format(self.config.hours)

    def get_alarm_period(self):
        if self.config.minutes:
            return self.config.minutes * 60
        return self.config.hours * 3600

    def upload_code_to_s3(self):
        s3_target_path = "s3://{bucket}/code/{file}".format(bucket=self.config.bucket,
                                                            file=self.get_code_zip_file_name())
        s3_upload_command = ["aws", "s3", "cp", self.get_code_zip_file_path(), s3_target_path]
        self.exec_aws_command(s3_upload_command)

    def is_deploy_needed(self):
        return (self.cli.command == 'update') or (self.cli.command == 'create')

    def is_start_stop_command(self):
        return (self.cli.command == 'start') or (self.cli.command == 'stop')

    def get_code_key_parameter(self):
        if self.is_deploy_needed():
            return "ParameterValue=code/{}".format(self.get_code_zip_file_name())
        else:
            return "UsePreviousValue=true"

    def get_parameter_value(self, value):
        if self.is_start_stop_command():
            return "UsePreviousValue=true"
        else:
            return "ParameterValue={}".format(value)

    def get_state_value(self):
        if self.cli.command == 'start':
            return 'ENABLED'
        if self.cli.command == 'stop':
            return 'DISABLED'

        if self.config.enabled:
            return 'ENABLED'
        else:
            return 'DISABLED'

    def add_template_parameters(self, command):
        command.append("--parameters")
        command.append("ParameterKey=Environment,ParameterValue={environment}".format(environment=self.cli.environment))
        command.append("ParameterKey=State,ParameterValue={state}".format(state=self.get_state_value())),
        command.append("ParameterKey=CodeS3Key,{}".format(self.get_code_key_parameter()))
        command.append("ParameterKey=Bucket,{}".format(self.get_parameter_value(self.config.bucket)))
        command.append("ParameterKey=CronExpression,{}".format(self.get_parameter_value(self.get_cron_expression())))
        command.append("ParameterKey=AlarmEnabled,{}".format(self.get_parameter_value(self.config.alarm_enabled)))
        if self.config.alarm_enabled:
            command.append("ParameterKey=AlarmEmail,{}".format(self.get_parameter_value(self.config.alarm_email)))
            command.append("ParameterKey=AlarmPeriod,{}".format(self.get_parameter_value(self.get_alarm_period())))
        return command

    def get_aws_cloudformation_command(self, subcommand):
        return [
            "aws", "cloudformation", subcommand, "--stack-name", self.get_stack_name(),
            "--template-body", "file://{}".format(os.path.join(cli_config.get_package_root_directory(), 'template.cfn.yml')),
            "--capabilities", "CAPABILITY_NAMED_IAM"
        ]

    def create_stack(self):
        create_stack_command = self.get_aws_cloudformation_command('create-stack')
        create_stack_command = self.add_template_parameters(create_stack_command)
        self.exec_aws_command(create_stack_command)

        wait_create_stack_command = [
            "aws", "cloudformation", "wait", "stack-create-complete",
            "--stack-name", self.get_stack_name()
        ]
        self.exec_aws_command(wait_create_stack_command)

    def update_stack(self):
        update_stack_command = self.get_aws_cloudformation_command('update-stack')
        update_stack_command = self.add_template_parameters(update_stack_command)
        self.exec_aws_command(update_stack_command)

        wait_update_stack_command = [
            "aws", "cloudformation", "wait", "stack-update-complete",
            "--stack-name", self.get_stack_name()
        ]
        self.exec_aws_command(wait_update_stack_command)

    def bucket_exists(self):
        check_bucket_command = ["aws", "s3api", "head-bucket", "--bucket", self.config.bucket]
        command_result = self.exec_aws_command(check_bucket_command)
        return command_result == 0

    def check_bucket(self):
        bucket_exists = self.bucket_exists()
        if self.cli.create_bucket:
            if bucket_exists:
                print "Bucket '{}' already exists".format(self.config.bucket)
                exit(1)
            else:
                print "Creating bucket '{}'".format(self.config.bucket)
                create_bucket_command = ["aws", "s3api", "create-bucket", "--bucket", self.config.bucket]
                self.exec_aws_command(create_bucket_command)
        else:
            if not bucket_exists:
                print "Bucket '{}' does not exist".format(self.config.bucket)
                exit(2)

    def create(self):
        self.check_bucket()
        self.zip_code()
        self.upload_code_to_s3()
        self.create_stack()

    def update(self):
        self.zip_code()
        self.upload_code_to_s3()
        self.update_stack()

    def start(self):
        self.update_stack()

    def stop(self):
        self.update_stack()

    def delete(self):
        delete_stack_command = [
            "aws", "cloudformation", "delete-stack",
            "--stack-name", self.get_stack_name()
        ]
        self.exec_aws_command(delete_stack_command)

        wait_update_stack_command = [
            "aws", "cloudformation", "wait", "stack-delete-complete",
            "--stack-name", self.get_stack_name()
        ]
        self.exec_aws_command(wait_update_stack_command)

        if self.cli.delete_bucket:
            delete_bucket_command = ["aws", "s3api", "delete-bucket", "--bucket", self.config.bucket]
            self.exec_aws_command(delete_bucket_command)

    def invoke(self):
        payload_content = "\"source\": \"LambdaCron-cli-invoke\", \"time\": \"{time}\", \"resources\": [\"Manual:invoke/LambdaCron-{environment}\"]".format(
            time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            environment=self.cli.environment
        )
        invoke_command = [
            "aws", "lambda", "invoke",
            "--invocation-type", "Event",
            "--function-name", self.get_stack_name(),
            "--payload", '{'+payload_content+'}',
            os.path.join(self.get_tmp_directory(), 'invoke_output.txt')
        ]
        self.exec_aws_command(invoke_command)

    def upload_tasks(self):
        upload_tasks_stack_command = [
            "aws", "s3", "sync", self.cli.directory, "s3://{}/tasks/".format(self.config.bucket), '--delete'
        ]
        self.exec_aws_command(upload_tasks_stack_command)

    def validate_task(self, schema, task_file_name):
        try:
            with open(task_file_name, 'r') as task_file:
                task = yaml.load(task_file)
            jsonschema.validate(task, schema)
        except Exception, ex:
            raise ex

    def validate(self):
        try:
            with open(cli_config.get_jsonschema_file_path(), 'r') as schema_file:
                schema = json.load(schema_file)

            if self.cli.task_file:
                self.validate_task(schema, self.cli.task_file)

            if self.cli.task_directory:
                all_yml_files = [os.path.join(dirpath, f)
                                 for dirpath, dirnames, files in os.walk(self.cli.task_directory)
                                 for f in files if f.endswith('.yml')]
                for file_name in all_yml_files:
                    self.validate_task(schema, file_name)
        except jsonschema.exceptions.ValidationError, ex:
            print("Validation failed! Validation error in task: {}".format(ex.message))
            sys.exit(1)
        except Exception, ex:
            raise ex
        print 'Validation success!'

    def print_summary(self):
        if self.config.is_environment_in_config_file():
            print "Environment found in LambdaCron config"
        else:
            print "Environment NOT found in LambdaCron config"

    def run(self):
        if self.is_config_required():
            self.print_summary()
        command_method = getattr(self, self.cli.command.replace('-', '_'))
        command_method()


def main():
    results = check_arg(sys.argv[1:])
    print results
    CliTool(results).run()