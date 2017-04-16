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
import json
import datetime
import pytz
from mock import patch
from lambda_cron.aws.lib.task_runner import TaskRunner, QueueTask, InvokeLambdaTask, HttpTask, BatchJobTask, DataPipelineJobTask
from lambda_cron.aws.lib.cron_checker import CronChecker


@pytest.fixture(scope="module")
def cron_checker():
    return CronChecker('2016-10-30T11:00:00Z', hour_period=1, minutes_period=0)


class SqsQueueSpy:
    def __init__(self):
        self.message_body = None
        self.messages_sent = 0

    def send_message(self, MessageBody):
        self.message_body = MessageBody
        self.messages_sent += 1


@pytest.fixture(scope="function")
def sqs_queue_spy():
    return SqsQueueSpy()


QUEUE_TASK_BODY =\
    {
        'type': 'queue',
        'QueueName': 'test-queue',
        'MessageBody': {
            'message_key_1': 'message_value_1',
            'message_key_2': ['message_value_2']
        }
    }


@pytest.fixture(scope="function")
def queue_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'task': dict(QUEUE_TASK_BODY)
    }


def test_expression_not_defined(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    queue_task_definition.pop('expression', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    exception_info.match(r'expression')


def test_type_not_defined(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    queue_task_definition['task'].pop('type', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    exception_info.match(r'type')


def test_task_not_defined(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    queue_task_definition.pop('task', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    exception_info.match(r'task')


def test_invalid_task_type(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    queue_task_definition['task']['type'] = 'unknown'
    with pytest.raises(AttributeError) as exception_info:
        task_runner.run(queue_task_definition)
    exception_info.match(r'TaskRunner instance has no attribute')


def test_invalid_task_definition(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    with pytest.raises(TypeError) as exception_info:
        task_runner.run('This is not a valid yaml')


@patch.object(QueueTask, 'get_queue')
def test_queue_should_run_basic(get_queue_mock, sqs_queue_spy, cron_checker, queue_task_definition):
    get_queue_mock.return_value = sqs_queue_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(queue_task_definition)

    assert sqs_queue_spy.messages_sent == 1
    assert sqs_queue_spy.message_body == json.dumps(QUEUE_TASK_BODY['MessageBody'])


@patch.object(QueueTask, 'get_queue')
def test_queue_should_not_by_time_run_basic(get_queue_mock, sqs_queue_spy, cron_checker, queue_task_definition):
    get_queue_mock.return_value = sqs_queue_spy
    queue_task_definition['expression'] = '0 9 * * *'

    task_runner = TaskRunner(cron_checker)
    task_runner.run(queue_task_definition)

    assert sqs_queue_spy.messages_sent == 0
    assert sqs_queue_spy.message_body is None


@patch.object(QueueTask, 'get_queue')
def test_queue_task_message_not_defined(get_queue_mock, sqs_queue_spy, cron_checker, queue_task_definition):
    get_queue_mock.return_value = sqs_queue_spy
    queue_task_definition['task'].pop('MessageBody', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    assert exception_info.match(r'MessageBody')


def test_queue_task_queue_not_defined(cron_checker, queue_task_definition):
    queue_task_definition['task'].pop('QueueName', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    assert exception_info.match(r'QueueName')


class LambdaClientSpy:
    def __init__(self):
        self.parameters = None
        self.calls = 0

    def invoke_async(self, **kwargs):
        self.parameters = kwargs
        self.calls += 1


@pytest.fixture(scope="function")
def lambda_client_spy():
    return LambdaClientSpy()


LAMBDA_TASK_BODY =\
    {
        'type': 'lambda',
        'FunctionName': 'testing-function',
        'InvokeArgs': {
            'my_input_1': 'value_input_1',
            'my_input_2': 2
        }
    }


@pytest.fixture(scope="function")
def lambda_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'task': dict(LAMBDA_TASK_BODY)
    }


@patch.object(InvokeLambdaTask, 'get_lambda_client')
def test_lambda_should_run_basic(get_lambda_client_mock, lambda_client_spy, cron_checker, lambda_task_definition):
    get_lambda_client_mock.return_value = lambda_client_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(lambda_task_definition)

    assert lambda_client_spy.calls == 1
    assert 'FunctionName' in lambda_client_spy.parameters
    assert lambda_client_spy.parameters['FunctionName'] == 'testing-function'
    assert 'InvokeArgs' in lambda_client_spy.parameters
    assert lambda_client_spy.parameters['InvokeArgs'] == json.dumps(LAMBDA_TASK_BODY['InvokeArgs'])


@patch.object(InvokeLambdaTask, 'get_lambda_client')
def test_lambda_should_not_by_time_run_basic(get_lambda_client_mock, lambda_client_spy, cron_checker, lambda_task_definition):
    get_lambda_client_mock.return_value = lambda_client_spy
    lambda_task_definition['expression'] = '0 9 * * *'

    task_runner = TaskRunner(cron_checker)
    task_runner.run(lambda_task_definition)

    assert lambda_client_spy.calls == 0
    assert lambda_client_spy.parameters == None


@patch.object(InvokeLambdaTask, 'get_lambda_client')
def test_lambda_task_function_name_not_defined(get_lambda_client_mock, lambda_client_spy, cron_checker, lambda_task_definition):
    get_lambda_client_mock.return_value = lambda_client_spy
    lambda_task_definition['task'].pop('FunctionName', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(lambda_task_definition)
    assert exception_info.match(r'FunctionName')


@patch.object(InvokeLambdaTask, 'get_lambda_client')
def test_lambda_task_invoke_args_not_defined(get_lambda_client_mock, lambda_client_spy, cron_checker, lambda_task_definition):
    get_lambda_client_mock.return_value = lambda_client_spy
    lambda_task_definition['task'].pop('InvokeArgs', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(lambda_task_definition)
    assert exception_info.match(r'InvokeArgs')


class HttpClientSpy:
    def __init__(self):
        self.args = None
        self.get_count = 0
        self.post_count = 0

    def get(self, **kwargs):
        self.args = kwargs
        self.get_count += 1

    def post(self, **kwargs):
        self.args = kwargs
        self.post_count += 1


@pytest.fixture(scope="function")
def http_client_spy():
    return HttpClientSpy()


HTTP_GET_TASK_BODY =\
    {
        'type': 'http',
        'method': 'GET',
        'request': {
            'url': 'http://lambda-cron.com/tests',
            'params': {
                'param_1': 'param_value_1',
                'param_2': 2
            }
        }
    }


HTTP_POST_TASK_BODY =\
    {
        'type': 'http',
        'method': 'POST',
        'request': {
            'url': 'http://lambda-cron.com/tests',
            'data': {
                'my_data_1': 'param_value_1',
                'my_data': 2
            }
        }
    }


@pytest.fixture(scope="function")
def http_get_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'task': dict(HTTP_GET_TASK_BODY)
    }


@pytest.fixture(scope="function")
def http_post_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'type': 'http',
        'task': dict(HTTP_POST_TASK_BODY)
    }


@patch.object(HttpTask, 'get_http_client')
def test_http_should_run_get_basic(get_requests_client_mock, http_client_spy, cron_checker, http_get_task_definition):
    get_requests_client_mock.return_value = http_client_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(http_get_task_definition)

    assert http_client_spy.get_count == 1
    assert http_client_spy.post_count == 0
    assert http_client_spy.args == http_get_task_definition['task']['request']


@patch.object(HttpTask, 'get_http_client')
def test_http_should_run_post_basic(get_requests_client_mock, http_client_spy, cron_checker, http_post_task_definition):
    get_requests_client_mock.return_value = http_client_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(http_post_task_definition)

    assert http_client_spy.get_count == 0
    assert http_client_spy.post_count == 1
    assert http_client_spy.args == http_post_task_definition['task']['request']


@patch.object(HttpTask, 'get_http_client')
def test_http_not_supported_method(get_requests_client_mock, http_client_spy, cron_checker, http_get_task_definition):
    get_requests_client_mock.return_value = http_client_spy
    http_get_task_definition['task']['method'] = 'put'

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(Exception) as exception_info:
        task_runner.run(http_get_task_definition)
    assert "Http method not supported: put" in str(exception_info.value)


class BatchClientSpy:
    def __init__(self):
        self.parameters = None
        self.calls = 0

    def submit_job(self, **kwargs):
        self.parameters = kwargs
        self.calls += 1


@pytest.fixture(scope="function")
def batch_client_spy():
    return BatchClientSpy()


BATCH_TASK_BODY =\
    {
        'type': 'batch',
        'jobName': 'testing-batch-job',
        'jobQueue': 'testing-batch-job-queue',
        'jobDefinition': 'testing-batch-job-definition',
        'parameters':
            {
                'param_1': 'value_1',
                'param_2': 'value_2'
            }
    }


@pytest.fixture(scope="function")
def batch_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'task': dict(BATCH_TASK_BODY)
    }


@patch.object(BatchJobTask, 'get_batch_client')
def test_batch_should_run_basic(get_batch_client_mock, batch_client_spy, cron_checker, batch_task_definition):
    get_batch_client_mock.return_value = batch_client_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(batch_task_definition)

    assert batch_client_spy.calls == 1
    assert 'jobName' in batch_client_spy.parameters
    assert batch_client_spy.parameters['jobName'] == 'testing-batch-job'
    assert 'jobQueue' in batch_client_spy.parameters
    assert batch_client_spy.parameters['jobQueue'] == 'testing-batch-job-queue'
    assert 'parameters' in batch_client_spy.parameters
    assert batch_client_spy.parameters['parameters'] == BATCH_TASK_BODY['parameters']


class DataPipelineClientSpy:
    def __init__(self):
        self.parameters = None
        self.calls = 0

    def activate_pipeline(self, **kwargs):
        self.parameters = kwargs
        self.calls += 1

@pytest.fixture(scope="function")
def datapipeline_client_spy():
    return DataPipelineClientSpy()


DATAPIPELINE_TASK_BODY =\
    {
        'type': 'datapipeline',
        'pipelineId': 'testing-pipeline-Id',
        'parameterValues':
            {
                'param_1': 'value_1',
                'param_2': 'value_2'
            },
        'startTimestamp': '2017-04-25T09:00:00Z',
    }


@pytest.fixture(scope="function")
def datapipeline_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'task': dict(DATAPIPELINE_TASK_BODY)
    }


@patch.object(DataPipelineJobTask, 'get_datapipeline_client')
def test_datapipeline_should_run_basic(get_datapipeline_client_mock, datapipeline_client_spy, cron_checker, datapipeline_task_definition):
    get_datapipeline_client_mock.return_value = datapipeline_client_spy
    datapipeline_task_definition['task'].pop('startTimestamp', None)

    task_runner = TaskRunner(cron_checker)
    task_runner.run(datapipeline_task_definition)

    assert datapipeline_client_spy.calls == 1
    assert 'pipelineId' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['pipelineId'] == 'testing-pipeline-Id'
    assert 'parameterValues' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['parameterValues'] == DATAPIPELINE_TASK_BODY['parameterValues']
    assert 'startTimestamp' not in datapipeline_client_spy.parameters


@patch.object(DataPipelineJobTask, 'get_datapipeline_client')
def test_datapipeline_should_run_start_time_iso8601(get_datapipeline_client_mock, datapipeline_client_spy, cron_checker, datapipeline_task_definition):
    get_datapipeline_client_mock.return_value = datapipeline_client_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(datapipeline_task_definition)

    assert datapipeline_client_spy.calls == 1
    assert 'pipelineId' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['pipelineId'] == 'testing-pipeline-Id'
    assert 'parameterValues' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['parameterValues'] == DATAPIPELINE_TASK_BODY['parameterValues']
    assert 'startTimestamp' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['startTimestamp'] == datetime.datetime(2017, 4, 25, 9, 0, 0, tzinfo=pytz.utc)


@patch.object(DataPipelineJobTask, 'get_datapipeline_client')
def test_datapipeline_should_run_start_time_no_iso8601(get_datapipeline_client_mock, datapipeline_client_spy, cron_checker, datapipeline_task_definition):
    get_datapipeline_client_mock.return_value = datapipeline_client_spy
    datapipeline_task_definition['task']['startTimestamp'] = '2017-04-25 09:00:00'

    task_runner = TaskRunner(cron_checker)
    task_runner.run(datapipeline_task_definition)

    assert datapipeline_client_spy.calls == 1
    assert 'pipelineId' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['pipelineId'] == 'testing-pipeline-Id'
    assert 'parameterValues' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['parameterValues'] == DATAPIPELINE_TASK_BODY['parameterValues']
    assert 'startTimestamp' in datapipeline_client_spy.parameters
    assert datapipeline_client_spy.parameters['startTimestamp'] == datetime.datetime(2017, 4, 25, 9, 0, 0)