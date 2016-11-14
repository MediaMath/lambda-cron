import os
import yaml


DEFAULT_BUCKET_PATTERN = 'LambdaCron-{environment}'


def get_project_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))


def get_lambda_cron_directory():
    return os.path.join(get_project_root_directory(), '../lambda-cron')


def get_lambda_cron_path(sub_path):
    return os.path.join(get_lambda_cron_directory(), sub_path)


def get_cli_config_file_path():
    return os.path.join(get_project_root_directory(), 'config/cli.yml')


class CliConfig:

    def __init__(self, environment):
        self.bucket = DEFAULT_BUCKET_PATTERN.format(environment=environment)

        self.config = None
        if os.path.exists(get_cli_config_file_path()):
            with open(get_cli_config_file_path(), 'w') as config_file:
                self.config = yaml.load(config_file)
            if environment in self.config:
                self.bucket = self.config[environment]['bucket']
            if 'all' in self.config:
                self.bucket = self.config['all']['bucket']+"-{}".format(environment)
