import json
import boto3
import logging


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


class Task:

    def __init__(self, task):
        self.task = task


class QueueTask(Task):

    def __init__(self, task):
        Task.__init__(self, task)
        self.queue = self.get_queue()

    def get_queue(self):
        queue_name = self.task['queue']
        sqs = boto3.resource('sqs')
        return sqs.get_queue_by_name(QueueName=queue_name)

    def run(self):
        return self.queue.send_message(MessageBody=json.dumps(self.task['message']))


class HttpTask(Task):

    def get_request(self, url):
        pass

    def post_request(self, url, parameters):
        pass

    def run(self):
        if self.task['method'] == 'get':
            self.get_request(self.task['url'])
        elif self.task['method'] == 'post':
            self.post_request(self.task['url'], self.task['parameters'])


class InvokeLambdaTask(Task):

    def __init__(self, task):
        Task.__init__(self, task)
        self.lambda_client = self.get_lambda_client()

    def get_lambda_client(self):
        return boto3.client('lambda')

    def run(self):
        return self.lambda_client.invoke_async(
            FunctionName=self.task['FunctionName'],
            InvokeArgs=json.dumps(self.task['InvokeArgs'])
        )
