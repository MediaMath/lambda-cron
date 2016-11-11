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

    def get_tmp_directory(self):
        return '/tmp/lambda_cron_{}'.format(self.environment)

    def get_dependencies_directory(self):
        return os.path.join(self.get_tmp_directory(), 'dependencies')

    def get_code_zip_file_path(self):
        return os.path.join(self.get_tmp_directory(), "code_{}.zip".format(int(round(time.time() * 1000))))

    def install_dependencies(self):
        pip_install_command = ["pip", "install", "--requirement", get_project_path('requirements.txt'), "--target",
                               self.get_dependencies_directory(), "--ignore-installed"]
        print pip_install_command
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


if __name__ == '__main__':
    results = check_arg(sys.argv[1:])
    print results
    lambda_cron_cli = LambdaCronCLI(results.environment)
    lambda_cron_cli.zip_code()

