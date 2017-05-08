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

import pytest
from lambda_cron.cli.cli_config import CliConfigParser, LambdaCronConfigFileNotFound, CliConfig
from tests.utils import valid_cong_file_path, valid_cong_file_path_only_prod_env

def test_config_file_not_foud():
    with pytest.raises(LambdaCronConfigFileNotFound) as exception_info:
        CliConfigParser('/file/that/not_exists.yml').get_config('prod')
    assert 'Config file not found: /file/that/not_exists.yml' in str(exception_info.value)


def test_should_use_custom_for_environment():
    config = CliConfigParser(valid_cong_file_path()).get_config('prod')
    assert config.bucket == 'test-bucket-custom'
    assert config.alarm_enabled
    assert config.alarm_email == 'my@email.com'
    assert config.minutes == 5
    assert not config.hours
    assert config.enabled


def test_should_use_for_all_environment():
    config = CliConfigParser(valid_cong_file_path()).get_config('other')
    assert config.bucket == 'test-bucket-all-other'
    assert not config.alarm_enabled
    assert config.alarm_email == ''
    assert not config.minutes
    assert config.hours == 2
    assert config.enabled


def test_should_use_custom_and_all_environment_2():
    config = CliConfigParser(valid_cong_file_path()).get_config('staging')
    assert config.bucket == 'test-bucket-all-staging'
    assert not config.alarm_enabled
    assert config.alarm_email == ''
    assert not config.minutes
    assert config.hours == 2
    assert config.enabled


def test_using_custom_settings():
    config = CliConfigParser(valid_cong_file_path()).get_config('develop')
    assert config.bucket == 'test-bucket-all-develop'
    assert config.alarm_enabled
    assert config.alarm_email == 'develop@email.com'
    assert not config.minutes
    assert config.hours == 1
    assert not config.enabled


def test_alarm_raise_exception_when_invalid_values_for_enabled():
    with pytest.raises(Exception) as exception_info:
        CliConfigParser(valid_cong_file_path()).get_config('alarm_enabled_bad_value')
    assert "Settings for 'alarm.enabled' must be a bool value" in str(exception_info.value)


def test_alarm_raise_exception_when_alarm_enabled_and_no_email():
    with pytest.raises(Exception) as exception_info:
        CliConfigParser(valid_cong_file_path()).get_config('alarm_enabled_no_email')
    assert "Email must be provided when alarm is enabled" in str(exception_info.value)


def test_enabled_raise_exception_when_invalid_values():
    with pytest.raises(Exception) as exception_info:
        CliConfigParser(valid_cong_file_path()).get_config('enabled_bad_value')
    assert "Settings for 'enabled' must be a bool value" in str(exception_info.value)


def test_frequency_raise_exeption_using_hours_and_minutes():
    with pytest.raises(Exception) as exception_info:
        CliConfigParser(valid_cong_file_path()).get_config('frequency_error_only_one')
    assert "Only one of 'hours' or 'minutes' must be used for the frequency ('every'). Both are not allowed." in str(exception_info.value)


def test_frequency_raise_with_float_value():
    config = CliConfigParser(valid_cong_file_path()).get_config('frequency_float')
    assert config.minutes == 5


def test_frequency_raise_exeption_invalid_time_key():
    with pytest.raises(Exception) as exception_info:
        CliConfigParser(valid_cong_file_path()).get_config('frequency_invalid_time_key')
    assert "Invalid time key used for frequency ('every'). Allowed keys: 'hours' or 'minutes'" in str(exception_info.value)


def test_should_use_global_default_settings():
    config = CliConfig('test')
    assert config.bucket == 'lambda-cron-test'
    assert not config.alarm_enabled
    assert config.alarm_email == ''
    assert not config.minutes
    assert config.hours == 1
    assert config.enabled


def test_environment_not_in_config_file():
    config = CliConfigParser(valid_cong_file_path_only_prod_env()).get_config('other')
    assert config.bucket == 'lambda-cron-other'
    assert config.enabled
    assert not config.alarm_enabled
    assert config.alarm_email == ''
    assert not config.minutes
    assert config.hours == 1
