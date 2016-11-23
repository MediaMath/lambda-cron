import os
import yaml


DEFAULT_BUCKET_PATTERN = 'LambdaCron-{environment}'


def get_project_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))


def get_cli_config_file_path():
    return os.path.join(get_project_root_directory(), 'config/cli.yml')


def load_config():
    if os.path.exists(get_cli_config_file_path()):
        with open(get_cli_config_file_path(), 'r') as config_file:
            return yaml.load(config_file)
    return None


class ConfigCli:

    def __init__(self, environment):
        self.environment = environment
        self.bucket = DEFAULT_BUCKET_PATTERN.format(environment=self.environment)
        self.alarm = False

        self.config = load_config()
        self.set_bucket()
        self.set_alarm()

    def set_alarm(self):
        if self.config and (self.environment in self.config) and ('alarm' in self.config[self.environment]):
            self.alarm = self.config[self.environment]['alarm']
        elif self.config and ('all' in self.config) and ('alarm' in self.config['all']):
            self.alarm = self.config['all']['alarm']

    def set_bucket(self):
        if self.config and (self.environment in self.config) and ('bucket' in self.config[self.environment]):
            self.bucket = self.config[self.environment]['bucket']
        elif self.config and ('all' in self.config) and ('bucket' in self.config['all']):
            if '{environment}' in self.config['all']['bucket']:
                self.bucket = self.config['all']['bucket'].format(environment=self.environment)
            else:
                self.bucket = self.config['all']['bucket'] + "-{}".format(self.environment)


