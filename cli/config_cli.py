import os
import yaml


DEFAULT_BUCKET_PATTERN = 'LambdaCron-{environment}'


def get_project_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))


def get_cli_config_file_path():
    return os.path.join(get_project_root_directory(), 'config/cli.yml')


class ConfigCli:

    def __init__(self, environment):
        self.bucket = DEFAULT_BUCKET_PATTERN.format(environment=environment)

        self.config = None
        if os.path.exists(get_cli_config_file_path()):
            with open(get_cli_config_file_path(), 'r') as config_file:
                self.config = yaml.load(config_file)
            if environment in self.config:
                self.bucket = self.config[environment]['bucket']
            elif 'all' in self.config:
                if '{environment}' in self.config['all']['bucket']:
                    print 'yeah !'
                    self.bucket = self.config['all']['bucket'].format(environment=environment)
                else:
                    self.bucket = self.config['all']['bucket']+"-{}".format(environment)
