""" Cron Lambda function
    This lambda function is designed to be executed periodically,
    read task definitions from a S3 bucket and if the cron expression
    in the tasks indicates is should be executed send it to an SQS queue.
"""
from __future__ import print_function

import boto3
import yaml
from croniter import croniter
from datetime import datetime, timedelta
import re
import json
import traceback


BUCKET_PATTERN = "lambda-cron.{}.mmknox"
QUEUE_PATTERN = "preakness-{}"
TASKS_PREFIX = 'tasks/'


class CronChecker:

    def __init__(self, current_timestamp, hour_period=1, minutes_period=0):
        self.start_of_period = self.get_start_of_period(current_timestamp)
        self.period = timedelta(hours=hour_period, minutes=minutes_period)

    def get_start_of_period(self, timestamp):
        """ Find the start of the current period
        Arguments:
        timestamp - ISO 8601 stamp string

        Retruns:
        Datetime objects for 1 second the start current evaluation period
        """
        actual_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        ideal_time = actual_time.replace(second=0)
        before_period = ideal_time - timedelta(seconds=1)
        return before_period

    def should_run(self, cron_expression):
        next_event = croniter(cron_expression, self.start_of_period).get_next(datetime)
        return (self.start_of_period < next_event and next_event <= (self.start_of_period + self.period))


class TaskRunner:
    def __init__(self, cron_checker, queue):
        self.cron_checker = cron_checker
        self.queue = queue

    def run(self, task_definition):
        if self.cron_checker.should_run(task_definition['expression']):
            self.queue.send_message(MessageBody=json.dumps(task_definition['message']))
            return True
        return False


def get_environment_from_event(event):
    m = re.search('LambdaCron-(\w*)-', event['resources'][0])
    if m and m.group(1) in ['sandbox', 'staging', 'prod']:
        return m.group(1)
    raise EnvironmentError('Invalid environment: '+m.group(1))


def handler(event, _):
    """ Main function """
    print(event)

    environment = get_environment_from_event(event)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_PATTERN.format(environment))
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QUEUE_PATTERN.format(environment))

    cron_checker = CronChecker(event['time'], hour_period=1, minutes_period=0)
    task_runner = TaskRunner(cron_checker, queue)

    for obj in bucket.objects.filter(Prefix=TASKS_PREFIX):
        if obj.key == TASKS_PREFIX:
            continue
        try:
            task_definition = yaml.load(obj.get()['Body'].read())
            if task_runner.run(task_definition):
                print("* Task fired: {}".format(task_definition['name']))
        except Exception, exc:
            print("! Error processing task: {}".format(obj.key))
            traceback.print_exc()
