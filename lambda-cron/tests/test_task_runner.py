import pytest
import json
from lib.task_runner import TaskRunner
from lib.cron_checker import CronChecker


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
def queue():
    return SqsQueueSpy()


@pytest.fixture(scope="function")
def base_task_definition():
    return {
        'name': 'Test task',
        'expression': '0 11 * * *',
        'message': MESSAGE_BODY
    }


def test_should_run_basic(cron_checker, queue, base_task_definition):
    task_runner = TaskRunner(cron_checker, queue)
    result = task_runner.run(base_task_definition)
    assert result is True
    assert queue.messages_sent == 1
    assert queue.message_body == json.dumps(MESSAGE_BODY)


def test_should_not_by_time_run_basic(cron_checker, queue, base_task_definition):
    task_runner = TaskRunner(cron_checker, queue)
    base_task_definition['expression'] = '0 9 * * *'
    result = task_runner.run(base_task_definition)
    assert result is False
    assert queue.messages_sent == 0
    assert queue.message_body is None


def test_expression_not_defined(cron_checker, queue, base_task_definition):
    task_runner = TaskRunner(cron_checker, queue)
    base_task_definition.pop('expression', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(base_task_definition)
    exception_info.match(r'expression')


def test_message_not_defined(cron_checker, queue, base_task_definition):
    task_runner = TaskRunner(cron_checker, queue)
    base_task_definition.pop('message', None)
    with pytest.raises(KeyError) as exception_info:
        task_runner.run(base_task_definition)
    exception_info.match(r'message')


def test_invalid_task_definition(cron_checker, queue, base_task_definition):
    task_runner = TaskRunner(cron_checker, queue)
    base_task_definition.pop('message', None)
    with pytest.raises(TypeError) as exception_info:
        task_runner.run('This is not a valid yaml')
