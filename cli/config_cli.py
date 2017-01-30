import os
import yaml


DEFAULT_BUCKET_PATTERN = 'lambda-cron-{environment}'


def get_project_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))


def get_cli_config_file_path():
    return os.path.expanduser('~/.lambdacron.yml')


def get_jsonschema_file_path():
    return os.path.join(get_project_root_directory(), 'schema.json')


def load_config():
    if os.path.exists(get_cli_config_file_path()):
        with open(get_cli_config_file_path(), 'r') as config_file:
            return yaml.load(config_file)
    return False


class ConfigCli:

    def __init__(self, environment):
        self.environment = environment
        self.bucket = DEFAULT_BUCKET_PATTERN.format(environment=self.environment)
        self.enabled = True
        self.alarm_enabled = False
        self.alarm_email = ''
        self.hours = 1
        self.minutes = False

        self.config = load_config()
        self.set_bucket()
        self.set_enabled()
        self.set_alarm()
        self.set_frequency()

    def is_environment_in_config_file(self):
        return self.config and (self.environment in self.config)

    def set_alarm(self):
        alarm_config = None
        if self.is_environment_in_config_file() and ('alarm' in self.config[self.environment]):
            alarm_config = self.config[self.environment]['alarm']
        elif self.config and ('all' in self.config) and ('alarm' in self.config['all']):
            alarm_config = self.config['all']['alarm']

        if not alarm_config:
            return

        self.alarm_enabled = alarm_config['enabled']
        if not isinstance(self.alarm_enabled, bool):
            raise Exception("Settings for 'alarm.enabled' must be a bool value")
        if self.alarm_enabled:
            if 'email' not in alarm_config:
                raise Exception("Email must be provided when alarm is enabled")
            self.alarm_email = alarm_config['email']

    def set_bucket(self):
        if self.is_environment_in_config_file() and ('bucket' in self.config[self.environment]):
            self.bucket = self.config[self.environment]['bucket']
        elif self.config and ('all' in self.config) and ('bucket' in self.config['all']):
            if '{environment}' in self.config['all']['bucket']:
                self.bucket = self.config['all']['bucket'].format(environment=self.environment)
            else:
                self.bucket = self.config['all']['bucket'] + "-{}".format(self.environment)

    def set_frequency(self):
        config_every = None
        if self.is_environment_in_config_file() and ('every' in self.config[self.environment]):
            config_every = self.config[self.environment]['every']
        elif self.config and ('all' in self.config) and ('every' in self.config['all']):
            config_every = self.config['all']['every']

        if not config_every:
            return

        if ('hours' in config_every) and ('minutes' in config_every):
            raise Exception("Only one of 'hours' or 'minutes' must be used for the frequency ('every'). Both are not allowed.")

        if 'hours' in config_every:
            self.hours = int(config_every['hours'])
            self.minutes = False
        if 'minutes' in config_every:
            self.minutes = int(config_every['minutes'])
            self.hours = False

    def set_enabled(self):
        if self.is_environment_in_config_file() and ('enabled' in self.config[self.environment]):
            self.enabled = self.config[self.environment]['enabled']
        elif self.config and ('all' in self.config) and ('enabled' in self.config['all']):
            self.enabled = self.config['all']['enabled']

        if not isinstance(self.enabled, bool):
            raise Exception("Settings for 'enabled' must be a bool value")
