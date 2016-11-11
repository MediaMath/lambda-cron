import argparse
import sys
import subprocess
import shutil
import os
import time
from zipfile import ZipFile


def check_arg(args=None):
    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(dest="command")
    deploy_command = commands_parser.add_parser('deploy')
    deploy_command.add_argument('-e', '--environment', required=True)
    deploy_command.add_argument('-s', '--state', default='DISABLED')
    return parser.parse_args(args)


def get_project_directory():
    return os.path.dirname(os.path.realpath(__file__))


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

    def __init__(self, environment):
        self.environment = environment
        self.timestamp = int(round(time.time() * 1000))

    def get_tmp_directory(self):
        return '/tmp/lambda_cron_{environment}'.format(environment=self.environment)

    def get_dependencies_directory(self):
        return os.path.join(self.get_tmp_directory(), 'dependencies')

    def get_code_zip_file_name(self):
        return "code_{}.zip".format(self.timestamp)

    def get_code_zip_file_path(self):
        return os.path.join(self.get_tmp_directory(), self.get_code_zip_file_name())

    def get_bucket_name(self):
        return "lambda-cron.{environment}.mmknox".format(environment=self.environment)

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
            zip_dir(zip_file, get_project_path('src'), 'src')
            zip_file.write(get_project_path('main.py'), 'main.py')

    def upload_code_to_s3(self):
        s3_target_path = "s3://{bucket}/code/{file}".format(bucket=self.get_bucket_name(),
                                                             file=self.get_code_zip_file_name())
        s3_upload_command = ["aws", "s3", "cp", self.get_code_zip_file_path(), s3_target_path]
        subprocess.call(s3_upload_command)

if __name__ == '__main__':
    results = check_arg(sys.argv[1:])
    print results
    lambda_cron_cli = LambdaCronCLI(results.environment)
    lambda_cron_cli.zip_code()
    lambda_cron_cli.upload_code_to_s3()

