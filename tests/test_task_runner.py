import pytest
import json
from mock import patch
from lambda_cron.lib.task_runner import TaskRunner, QueueTask
from lambda_cron.lib.cron_checker import CronChecker

MESSAGE_BODY =\
    {
        'message_key_1': 'message_value_1',
        'message_key_2': ['message_value_2']
    }


class SqsQueueSpy:
    def __init__(self):
        self.message_body = None
        self.messages_sent = 0

    def send_message(self, MessageBody):
        self.message_body = MessageBody
        self.messages_sent += 1


@pytest.fixture(scope="module")
def cron_checker():
    return CronChecker('2016-10-30T11:00:00Z', hour_period=1, minutes_period=0)


@pytest.fixture(scope="function")
def sqs_queue_spy():
    return SqsQueueSpy()


@pytest.fixture(scope="function")
def queue_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'type': 'queue',
        'task': {
            'queue': 'test-queue',
            'message': MESSAGE_BODY
        }
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
    queue_task_definition.pop('message', None)
    with pytest.raises(TypeError) as exception_info:
        task_runner.run('This is not a valid yaml')


@patch.object(QueueTask, 'get_queue')
def test_should_run_basic(get_queue_mock, sqs_queue_spy, cron_checker, queue_task_definition):
    get_queue_mock.return_value = sqs_queue_spy

    task_runner = TaskRunner(cron_checker)
    task_runner.run(queue_task_definition)

    assert sqs_queue_spy.messages_sent == 1
    assert sqs_queue_spy.message_body == json.dumps(MESSAGE_BODY)


@patch.object(QueueTask, 'get_queue')
def test_should_not_by_time_run_basic(get_queue_mock, sqs_queue_spy, cron_checker, queue_task_definition):
    get_queue_mock.return_value = sqs_queue_spy

    task_runner = TaskRunner(cron_checker)
    queue_task_definition['expression'] = '0 9 * * *'
    task_runner.run(queue_task_definition)

    assert sqs_queue_spy.messages_sent == 0
    assert sqs_queue_spy.message_body is None


def test_task_queue_not_defined(cron_checker, queue_task_definition):
    task_runner = TaskRunner(cron_checker)
    queue_task_definition['task'].pop('queue', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(queue_task_definition)
    exception_info.match(r'queue')
