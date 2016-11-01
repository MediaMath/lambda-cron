""" Cron Lambda function
    This lambda function is designed to be executed periodically,
    read task definitions from a S3 bucket and if the cron expression
    in the tasks indicates is should be executed send it to an SQS queue.
"""
from __future__ import print_function

import boto3
import yaml
import re
import traceback
from src.cron_checker import CronChecker
from src.task_runner import TaskRunner


BUCKET_PATTERN = "lambda-cron.{}.mmknox"
QUEUE_PATTERN = "preakness-{}"
TASKS_PREFIX = 'tasks/'


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
