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


BUCKET = "lambdacron-taskstoragebucket-1dnoooztm6rn0"
QUEUE  = "LambdaCron-TaskQueue-3WCGEQEF3BCA"


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
        if self.start_of_period < next_event and next_event <= (self.start_of_period + self.period):
            return True
        return False


def handler(event, _):
    """ Main function """
    print(event)
    cron_checker = CronChecker(event['time'], hour_period=1, minutes_period=0)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET)

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QUEUE)

    for obj in bucket.objects.all():
        task = yaml.load(obj.get()['Body'].read())
        print(task)
        if cron_checker.should_run(task['expression']):
            print("{} fired".format(task['name']))
            queue.send_message(MessageBody="{} fired".format(task['name']))

            print("**********\n")
