import json
import boto3
import logging
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TaskRunner:
    def __init__(self, cron_checker):
        self.cron_checker = cron_checker

    def run(self, task):
        if self.cron_checker.should_run(task['expression']):
            command_method = getattr(self, "get_{}_task_runner".format(task['type'].lower()))
            response = command_method(task['task']).run()
            logger.info('Task executed')
            logger.info(response)

    def get_queue_task_runner(self, task):
        return QueueTask(task)

    def get_lambda_task_runner(self, task):
        return InvokeLambdaTask(task)

    def get_http_task_runner(self, task):
        return HttpTask(task)


class Task:

    def __init__(self, task):
        self.task = task


class QueueTask(Task):

    def get_queue(self):
        queue_name = self.task['QueueName']
        sqs = boto3.resource('sqs')
        return sqs.get_queue_by_name(QueueName=queue_name)

    def run(self):
        return self.get_queue().send_message(MessageBody=json.dumps(self.task['MessageBody']))


class HttpTask(Task):

    def get_http_client(self):
        return requests

    def run(self):
        if self.task['method'].lower() == 'get':
            return self.get_http_client().get(**self.task['request'])
        elif self.task['method'].lower() == 'post':
            return self.get_http_client().post(**self.task['request'])
        else:
            raise Exception("Http method not supported: {}".format(self.task['method'].lower()))


class InvokeLambdaTask(Task):

    def get_lambda_client(self):
        return boto3.client('lambda')

    def run(self):
        return self.get_lambda_client().invoke_async(
            FunctionName=self.task['FunctionName'],
            InvokeArgs=json.dumps(self.task['InvokeArgs'])
        )
