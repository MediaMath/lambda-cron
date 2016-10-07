import pytest
import json
import main


def test_get_environment_staging():
    event = {'resources': ['arn:aws:events:us-east-1:438025690015:rule/LambdaCron-hourly-staging']}
    assert main.get_environment_from_event(event) == 'staging'

def test_get_environment_sandbox():
    event = {'resources': ['arn:aws:events:us-east-1:438025690015:rule/LambdaCron-hourly-sandbox']}
    assert main.get_environment_from_event(event) == 'sandbox'

def test_get_environment_prod():
    event = {'resources': ['arn:aws:events:us-east-1:438025690015:rule/LambdaCron-hourly-prod']}
    assert main.get_environment_from_event(event) == 'prod'

def test_get_environment_error():
    event = {'resources': ['arn:aws:events:us-east-1:438025690015:rule/LambdaCron-hourly-other']}
    with pytest.raises(EnvironmentError) as exception_info:
        main.get_environment_from_event(event)
    assert 'Invalid environment: other' in str(exception_info.value)