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


DEFAULT_BUCKET_PATTERN = 'lambda-cron-{environment}'


def get_package_root_directory():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))


def get_cli_config_file_path():
    return os.path.expanduser('~/.lambda-cron.yml')


def get_jsonschema_file_path():
    return os.path.join(get_package_root_directory(), 'schema.json')


def load_config():
    if os.path.exists(get_cli_config_file_path()):
        with open(get_cli_config_file_path(), 'r') as config_file:
            return yaml.load(config_file)
    return False


class CliConfig:

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

    def is_custom_options(self, option):
        return self.is_environment_in_config_file() and (option in self.config[self.environment])

    def is_global_option(self, option):
        return self.config and ('all' in self.config) and (option in self.config['all'])

    def get_config_option(self, option):
        option_value = None
        if self.is_custom_options(option):
            option_value = self.config[self.environment][option]
        elif self.is_global_option(option):
            option_value = self.config['all'][option]
        return option_value

    def set_alarm(self):
        alarm_config = self.get_config_option('alarm')

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
        if self.is_custom_options('bucket'):
            self.bucket = self.config[self.environment]['bucket']
        elif self.is_global_option('bucket'):
            if '{environment}' in self.config['all']['bucket']:
                self.bucket = self.config['all']['bucket'].format(environment=self.environment)
            else:
                self.bucket = self.config['all']['bucket'] + "-{}".format(self.environment)

    def get_time_key_value(self, config_every):
        time_key = None
        if 'hours' in config_every:
            time_key = 'hours'

        if 'minutes' in config_every:
            if time_key is not None:
                raise Exception("Only one of 'hours' or 'minutes' must be used for the frequency ('every'). Both are not allowed.")
            time_key = 'minutes'

        if time_key is None:
            raise Exception("Invalid time key used for frequency ('every'). Allowed keys: 'hours' or 'minutes'")

        return time_key, int(config_every[time_key])

    def set_frequency(self):
        config_every = self.get_config_option('every')
        if not config_every:
            return

        time_key, time_value = self.get_time_key_value(config_every)
        self.hours = False
        self.minutes = False
        setattr(self, time_key, time_value)

    def set_enabled(self):
        enabled_default_value = self.enabled
        self.enabled = self.get_config_option('enabled')
        if self.enabled is None:
            self.enabled = enabled_default_value

        if not isinstance(self.enabled, bool):
            raise Exception("Settings for 'enabled' must be a bool value")
