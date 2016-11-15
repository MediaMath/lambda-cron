[![Build Status](https://travis-ci.com/MediaMath/knox-lambda-cron.svg?token=tMt81cZ8XUGin1RurU5s&branch=master)](https://travis-ci.com/MediaMath/knox-lambda-cron)
# LambdaCron

Project to run scheduled tasks using lambda functions on AWS.

Lambda function will run periodically (can be customized) and it will run
the tasks scheduled for current period.

**LambdaCron** provide different type of actions to trigger with the tasks:

* Send message to SQS queue.
* Invoke lambda function.
* HTTP requests (GET & POST)

Tasks are YAML files stored on a S3 bucket and they will define frequency
of the task (cron expression) and the action to do.

## LambdaCron CLI

**LambdaCron** provide a CLI tool that allow to run multiple environments
with different settings.

Some of the setting that are allowed to set are:

* Bucket to store tasks and lambda function code.
* Frequency

This settings can be customized for each environment. As many environments
as desired can be set up.

### CLI commands

* **create**: Create new **LambdaCron** environment in the AWS account
  * **--environment (-e)**: Environment to work with (string)
  * **--state (-s)**: State of the lambda event (ENABLED | DISABLED) (optional)
* **update**: Update new settings for the environment.
  * **--environment (-e)**: Environment to work with (string)
  * **--state (-s)**: State of the lambda event (ENABLED | DISABLED) (optional)
* **invoke**: Invoke lambda function manually
  * **--environment (-e)**: Environment to work with (string)
* **delete**: Delete **LambdaCron** environment from the AWS account
  * **--environment (-e)**: Environment to work with (string)

## Tasks

``` yaml
name: sample name
expression: "0 2 * * *"
task:
  key1: value 1
  key2: value 2
```

## Development

#### CloudFormation
Project is running 100% with AWS resources and they are defined using CloudFormation.
The the template defined a stack will be created in AWS and it will be managed using
CloudFormation tools.

### Requirements
- Python 2.7
- Virtual Environment
- pip
- Boto3
  - Boto3 is installed as part of the lambda functions Environment.  To aviod the overhead of including it in your deployment artifact install boto3 on your system instead of in the virtual environment
- awscli (configured)

## TODO

* Cron:
    * Task to invoke Lambda functions
    * Task to send HTTP requests
    * Allow customized frequency
    * Template system for task definitions.
* CLI
    * Allow customized frequency
    * Allow to use different AWS profiles.
    