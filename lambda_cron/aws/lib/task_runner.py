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

import json
import boto3
import logging
import requests
import dateutil.parser


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TaskRunner:
    def __init__(self, cron_checker):
        self.cron_checker = cron_checker

    def run(self, task):
        if self.cron_checker.should_run(task['expression']):
            command_method = getattr(self, "get_{}_task_runner".format(task['task']['type'].lower()))
            response = command_method(task['task']).run()
            logger.info('Task executed!')
            logger.info(response)

    def get_queue_task_runner(self, task):
        return QueueTask(task)

    def get_lambda_task_runner(self, task):
        return InvokeLambdaTask(task)

    def get_http_task_runner(self, task):
        return HttpTask(task)

    def get_batch_task_runner(self, task):
        return BatchJobTask(task)

    def get_datapipeline_task_runner(self, task):
        return DataPipelineJobTask(task)


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


class BatchJobTask(Task):

    def get_batch_client(self):
        return boto3.client('batch')

    def run(self):
        self.task.pop('type')
        self.get_batch_client().submit_job(**self.task)


class DataPipelineJobTask(Task):

    def get_datapipeline_client(self):
        return boto3.client('datapipeline')

    def run(self):
        self.task.pop('type')
        if 'startTimestamp' in self.task:
            self.task['startTimestamp'] = dateutil.parser.parse(self.task['startTimestamp'])
        self.get_datapipeline_client().activate_pipeline(**self.task)
