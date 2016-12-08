import pytest
import json
from mock import patch
from lambda_cron.lib.task_runner import TaskRunner, QueueTask, InvokeLambdaTask
from lambda_cron.lib.cron_checker import CronChecker


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
        'queue': 'test-queue',
        'message': {
            'message_key_1': 'message_value_1',
            'message_key_2': ['message_value_2']
        }
    }


@pytest.fixture(scope="function")
def queue_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'type': 'queue',
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
    queue_task_definition.pop('type', None)
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
    queue_task_definition['type'] = 'unknown'
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
    assert sqs_queue_spy.message_body == json.dumps(QUEUE_TASK_BODY['message'])


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
    queue_task_definition['task'].pop('message', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    assert exception_info.match(r'message')


def test_queue_task_queue_not_defined(cron_checker, queue_task_definition):
    queue_task_definition['task'].pop('queue', None)

    task_runner = TaskRunner(cron_checker)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    assert exception_info.match(r'queue')


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
        'type': 'lambda',
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
        self.get = 0
        self.post = 0

    def get(self, **kwargs):
        self.args = kwargs
        self.get += 1

    def post(self, **kwargs):
        self.args = kwargs
        self.post += 1


HTTP_GET_TASK_BODY =\
    {
        'method': 'GET',
        'request': {
            'url': 'http://lambda-cron.com/tests',
            'params': {
                'param_1': 'param_value_1',
                'param_2': 2
            }
        }
    }


@pytest.fixture(scope="function")
def http_get_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'type': 'http',
        'task': dict(HTTP_GET_TASK_BODY)
    }
