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

import logging
import boto3
import yaml
import os
import traceback
from lib.cron_checker import CronChecker
from lib.task_runner import TaskRunner

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TASKS_PREFIX = 'tasks/'


def read_config():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yml'), 'r') as config_file:
        return yaml.load(config_file)


CONFIG = read_config()


def handler(event, _):
    """ Main function """
    logger.info(event)

    logger.info(CONFIG)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(CONFIG['bucket'])

    cron_checker = CronChecker(event['time'],
                               hour_period=CONFIG['frequency']['hours'],
                               minutes_period=CONFIG['frequency']['minutes'])
    task_runner = TaskRunner(cron_checker)

    for obj in bucket.objects.filter(Prefix=TASKS_PREFIX):
        if obj.key == TASKS_PREFIX:
            continue
        try:
            task_definition = yaml.load(obj.get()['Body'].read())
            logger.info("Running task: {}".format(task_definition['name']))
            task_runner.run(task_definition)
        except:
            logger.error("!! Error processing task: {}".format(obj.key))
            traceback.print_exc()
