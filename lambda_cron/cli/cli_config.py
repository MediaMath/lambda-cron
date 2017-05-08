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


def get_default_cli_config_file_path():
    return os.path.expanduser('~/.lambda-cron.yml')


class LambdaCronConfigFileNotFound(Exception):
    pass


def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as config_file:
            return yaml.load(config_file)
    raise LambdaCronConfigFileNotFound('Config file not found: {}'.format(file_path))


class CliConfigParser:

    DEFAULT_ENABLED = True
    DEFAULT_ALARM_ENABLED = False
    DEFAULT_ALARM_EMAIL = ''

    def __init__(self, config_file_path):
        self.file_config = load_config(config_file_path)
        self.environment = None

    def get_config(self, environment):
        self.environment = environment
        cli_config = CliConfig(self.environment)
        cli_config.bucket = self._get_bucket()
        cli_config.enabled = self._get_enabled()
        cli_config.alarm_enabled, cli_config.alarm_email = self._get_alarm()
        self._set_frequency(cli_config)
        return cli_config

    def _is_environment_in_config_file(self):
        return self.file_config and (self.environment in self.file_config)

    def _is_custom_options(self, option):
        return self._is_environment_in_config_file() and (option in self.file_config[self.environment])

    def _is_global_option(self, option):
        return self.file_config and ('all' in self.file_config) and (option in self.file_config['all'])

    def _get_config_option(self, option):
        option_value = None
        if self._is_custom_options(option):
            option_value = self.file_config[self.environment][option]
        elif self._is_global_option(option):
            option_value = self.file_config['all'][option]
        return option_value

    def _get_alarm(self):
        alarm_config = self._get_config_option('alarm')

        if not alarm_config:
            return self.DEFAULT_ALARM_ENABLED, self.DEFAULT_ALARM_EMAIL

        alarm_enabled = alarm_config['enabled']
        if not isinstance(alarm_enabled, bool):
            raise Exception("Settings for 'alarm.enabled' must be a bool value")
        alarm_email = self.DEFAULT_ALARM_EMAIL
        if alarm_enabled:
            if 'email' not in alarm_config:
                raise Exception("Email must be provided when alarm is enabled")
            alarm_email = alarm_config['email']

        return alarm_enabled, alarm_email

    def _get_bucket(self):
        if self._is_custom_options('bucket'):
            return self.file_config[self.environment]['bucket']
        elif self._is_global_option('bucket'):
            if '{environment}' in self.file_config['all']['bucket']:
                return self.file_config['all']['bucket'].format(environment=self.environment)
            else:
                return self.file_config['all']['bucket'] + "-{}".format(self.environment)
        else:
            return DEFAULT_BUCKET_PATTERN.format(environment=self.environment)

    @staticmethod
    def _get_time_key_value(config_every):
        time_key = None
        if 'hours' in config_every:
            time_key = 'hours'

        if 'minutes' in config_every:
            if time_key is not None:
                raise Exception(
                    "Only one of 'hours' or 'minutes' must be used for the frequency ('every'). Both are not allowed.")
            time_key = 'minutes'

        if time_key is None:
            raise Exception("Invalid time key used for frequency ('every'). Allowed keys: 'hours' or 'minutes'")

        return time_key, int(config_every[time_key])

    def _set_frequency(self, cli_config):
        config_every = self._get_config_option('every')
        if not config_every:
            return

        cli_config.hours = cli_config.minutes = False
        time_key, time_value = self._get_time_key_value(config_every)
        setattr(cli_config, time_key, time_value)

    def _get_enabled(self):
        enabled = self._get_config_option('enabled')
        if enabled is None:
            return self.DEFAULT_ENABLED

        if not isinstance(enabled, bool):
            raise Exception("Settings for 'enabled' must be a bool value")

        return enabled


class CliConfig:

    def __init__(self, environment):
        self.environment = environment
        self.bucket = DEFAULT_BUCKET_PATTERN.format(environment=self.environment)
        self.enabled = True
        self.alarm_enabled = False
        self.alarm_email = ''
        self.hours = 1
        self.minutes = False
