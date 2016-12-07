""" Cron Lambda function
    This lambda function is designed to be executed periodically,
    read task definitions from a S3 bucket and if the cron expression
    in the tasks indicates is should be executed send it to an SQS queue.
"""

import logging
import boto3
import yaml
import os
import traceback
from lib.cron_checker import CronChecker
from lib.task_runner import TaskRunner

logger = logging.getLogger()
logger.setLevel(logging.INFO)

QUEUE_PATTERN = "preakness-{}"
TASKS_PREFIX = 'tasks/'


def read_config():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yml'), 'r') as config_file:
        return yaml.load(config_file)


def handler(event, _):
    """ Main function """
    logger.info(event)

    config = read_config()
    logger.info(config)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(config['bucket'])

    cron_checker = CronChecker(event['time'], hour_period=1, minutes_period=0)
    task_runner = TaskRunner(cron_checker)

    for obj in bucket.objects.filter(Prefix=TASKS_PREFIX):
        if obj.key == TASKS_PREFIX:
            continue
        try:
            task_definition = yaml.load(obj.get()['Body'].read())
            if task_runner.run(task_definition):
                logger.info("** Task fired: {}".format(task_definition['name']))
        except Exception, exc:
            logger.error("!! Error processing task: {}".format(obj.key))
            traceback.print_exc()
