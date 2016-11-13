import argparse
import sys
import subprocess
import shutil
import os
import time
import datetime
from zipfile import ZipFile


def check_arg(args=None):
    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(dest="command")

    deploy_command = commands_parser.add_parser('create')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-s', '--state', default='DISABLED')

    deploy_command = commands_parser.add_parser('deploy')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-s', '--state', default='DISABLED')

    deploy_command = commands_parser.add_parser('update')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-s', '--state', default='DISABLED')

    return parser.parse_args(args)


def get_project_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lambda-cron'))


def get_project_path(sub_path):
    return os.path.join(get_project_directory(), sub_path)


def zip_dir(zip_file, path, prefix=''):
    for root, dirs, files in os.walk(path):
        for file in files:
            absolute_path = os.path.join(root, file)
            relative_path = absolute_path[len(path) + len(os.sep):]
            if prefix:
                relative_path = os.path.join(prefix, relative_path)
            zip_file.write(absolute_path, relative_path)


class LambdaCronCLI:

    def __init__(self, cli_instructions):
        self.cli = cli_instructions
        self.timestamp = int(round(time.time() * 1000))

    def get_tmp_directory(self):
        return '/tmp/lambda_cron_{environment}'.format(environment=self.cli.environment)

    def get_dependencies_directory(self):
        return os.path.join(self.get_tmp_directory(), 'dependencies')

    def get_code_zip_file_name(self):
        return "code_{}.zip".format(self.timestamp)

    def get_code_zip_file_path(self):
        return os.path.join(self.get_tmp_directory(), self.get_code_zip_file_name())

    def get_stack_name(self):
        return "LambdaCron-{environment}".format(environment=self.cli.environment)

    def get_bucket_name(self):
        return "lambda-cron.{environment}.mmknox".format(environment=self.cli.environment)

    def install_dependencies(self):
        pip_install_command = ["pip", "install", "--requirement", get_project_path('requirements.txt'), "--target",
                               self.get_dependencies_directory(), "--ignore-installed"]
        os.mkdir(self.get_dependencies_directory())
        subprocess.call(pip_install_command)

    def zip_code(self):
        tmp_directory = self.get_tmp_directory()
        if os.path.exists(tmp_directory):
            shutil.rmtree(tmp_directory)
        os.mkdir(tmp_directory)
        self.install_dependencies()
        with ZipFile(self.get_code_zip_file_path(), 'w') as zip_file:
            zip_dir(zip_file, self.get_dependencies_directory())
            zip_dir(zip_file, get_project_path('lib'), 'lib')
            zip_file.write(get_project_path('main.py'), 'main.py')

    def upload_code_to_s3(self):
        s3_target_path = "s3://{bucket}/code/{file}".format(bucket=self.get_bucket_name(),
                                                             file=self.get_code_zip_file_name())
        s3_upload_command = ["aws", "s3", "cp", self.get_code_zip_file_path(), s3_target_path]
        subprocess.call(s3_upload_command)

    def create_stack(self):
        update_stack_command = [
            "aws", "cloudformation", "create-stack", "--stack-name", self.get_stack_name(),
            "--template-body", "file://{}".format(get_project_path('template.cfn.yml')),
            "--parameters", self.get_code_key_parameter(is_new_deploy=True),
            "ParameterKey=Environment,ParameterValue={environment}".format(environment=self.cli.environment),
            "ParameterKey=State,ParameterValue={state}".format(state=self.cli.state),
            "--capabilities", "CAPABILITY_NAMED_IAM", "--region", "us-east-1"
        ]
        print update_stack_command
        subprocess.call(update_stack_command)
        wait_update_stack_command = [
            "aws", "cloudformation", "wait", "stack-create-complete",
            "--stack-name", self.get_stack_name(),
            "--region", "us-east-1"
        ]
        subprocess.call(wait_update_stack_command)

    def get_code_key_parameter(self, is_new_deploy=False):
        if is_new_deploy:
            return "ParameterKey=CodeS3Key,ParameterValue=code/{}".format(self.get_code_zip_file_name())
        else:
            return "ParameterKey=CodeS3Key,UsePreviousValue=true"

    def update_stack(self, is_new_deploy=False):
        update_stack_command = [
            "aws", "cloudformation", "update-stack", "--stack-name", self.get_stack_name(),
            "--template-body", "file://{}".format(get_project_path('template.cfn.yml')),
            "--parameters", self.get_code_key_parameter(is_new_deploy),
            "ParameterKey=Environment,ParameterValue={environment}".format(environment=self.cli.environment),
            "ParameterKey=State,ParameterValue={state}".format(state=self.cli.state),
            "--capabilities", "CAPABILITY_NAMED_IAM", "--region", "us-east-1"
        ]
        print update_stack_command
        subprocess.call(update_stack_command)
        wait_update_stack_command = [
            "aws", "cloudformation", "wait", "stack-update-complete",
            "--stack-name", self.get_stack_name(),
            "--region", "us-east-1"
        ]
        subprocess.call(wait_update_stack_command)

    def create(self):
        print get_project_directory()
        self.zip_code()
        # self.upload_code_to_s3()
        # self.create_stack()

    def deploy(self):
        self.zip_code()
        self.upload_code_to_s3()
        self.update_stack(is_new_deploy=True)

    def update(self):
        self.update_stack()

    def invoke(self):
        payload = "{\"source\": \"FINP Dev\", \"time\": \"${time}\", \"resources\": [\"Manual:invoke/LambdaCron-${environment}-LambdaCronHourlyEvent-ZZZ\"]}".format(
            time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            environment=self.cli.environment
        )
        invoke_command = [
            "aws", "lambda", "invoke",
            "--invocation-type", "Event",
            "--function-name", "LambdaCron-${environment}".format(environment=self.cli.environment),
            "--payload", payload,
            os.path.join(self.get_tmp_directory(), 'invoke_output.txt')
        ]
        subprocess.call(invoke_command)

    def run(self):
        command_method = getattr(self, self.cli.command)
        command_method()


if __name__ == '__main__':
    results = check_arg(sys.argv[1:])
    print results
    LambdaCronCLI(results).run()



