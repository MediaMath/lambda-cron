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


PERIOD = timedelta(hours=1)
BUCKET = "lambdacron-taskstoragebucket-1dnoooztm6rn0"
QUEUE  = "LambdaCron-TaskQueue-3WCGEQEF3BCA"

def start_of_period(timestamp):
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



def handler(event, _):
    """ Main function """
    print(event)
    start = start_of_period(event['time'])

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET)

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QUEUE)

    for obj in bucket.objects.all():
        task = yaml.load(obj.get()['Body'].read())
        print(task)
        next_event = croniter(task['expression'], start).get_next(datetime)
        print(next_event)
        if start < next_event and next_event <= start + PERIOD:
            print("{} fired".format(task['name']))
            queue.send_message(MessageBody="{} fired".format(task['name']))

            print("**********\n")
