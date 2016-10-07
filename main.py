""" Cron Lambda function
    This lambda function is designed to be exected at the start of each hour,
    read task definistions from a lambda bucket and if the cron expression
    in the tasks indicates is should be executed in the next hour send
    it to an SQS queue.
"""
from __future__ import print_function

import boto3
import yaml
from croniter import croniter
from datetime import datetime, timedelta
import re


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


def get_environment_from_event(event):
    m = re.search('-(\w*)$', event['resources'][0])
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

    for obj in bucket.objects.filter(Prefix=TASKS_PREFIX):
        if obj.key == TASKS_PREFIX: continue
        task = yaml.load(obj.get()['Body'].read())
        print(task)
        if cron_checker.should_run(task['expression']):
            print(" {} fired".format(task['name']))
            queue.send_message(MessageBody=task['message'])
            print("**********\n")
