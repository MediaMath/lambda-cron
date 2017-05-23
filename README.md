[![Build Status](https://travis-ci.com/MediaMath/lambda-cron.svg?token=tMt81cZ8XUGin1RurU5s&branch=master)](https://travis-ci.com/MediaMath/lambda-cron)
# LambdaCron

![LambdaCron](./lambda-cron-diagram.png "LambdaCron")

**LambdaCron** is a serverless cron tool. It provides a way to run scheduled tasks
on the AWS cloud, all managed by a command line tool ([LambdaCron CLI](#lambdacron-cli)).

Tasks are scheduled using the same syntax for expressions as Linux
[crontab](https://help.ubuntu.com/community/CronHowto).

**LambdaCron** offers 4 different types of tasks:

* **Queue task**: send message to AWS SQS queue.
* **Lambda task**: invoke AWS Lambda function.
* **Batch task**: submit AWS Batch job.
* **HTTP task**: send HTTP requests (GET & POST).

Tasks are defined in YAML files and are stored in a S3 bucket.

## LambdaCron CLI

**LambdaCron** provides a CLI tool that allows management of your cron tasks without access
to the AWS Console.  It also allows creation of multiple environments with different settings.

### Settings

Custom settings for environments are set in a YAML-formatted configuration file located in the
user home directory, and must be named **~/.lambda-cron.yml**.

There are 3 levels of preferences for settings:

* Environment: Custom values for an specific environment.
* Global: Custom values that will have effect to all environments created.
* Default: Default values in case no custom values are specified (by environment or globally)

Highest level of preference is *Environment*, followed by *Global* and finally *Default*. Each option
in the settings can set the value from different levels. Higher level of preference overwrite lower levels.

Each environment is defined with a root key in the YAML, while global settings are identified with the
key *global*.

Options available:

#### bucket

Name of the bucket where Lambda function code will be hosted and tasks stored.

```yaml
bucket: 'my-custom-bucket-name'
```

You can use the macro, **{environment}**, in the string for the bucket, and it will
be replaced by the environment name.

**Default**: lambda-cron-{environment}

The bucket will have two folders:

* code/
* tasks/

#### every (frequency)

Frequency at which the Lambda function will execute to run tasks.
It indicates the frequency in **minutes OR hours** with an integer number.
It is specified with one of the following parameters:

* minutes
* hours

```yaml
every:
    minutes: 5
```

**Default**: every hour.

More info for [frequency](#frequency).

#### alarm

Alarm can be set up using CloudWatch metrics. It uses the following parameters:

* enabled
* email (Required if alarm is enabled).

```yaml
alarm:
    enabled: True
    email: my-mailing-list@email.com
```

**Default**: disabled.

#### enabled

It enables/disables the cron (CloudWatch event).

```yaml
enabled: True
```

**Default**: enabled.

#### Example

```yaml
global:
  bucket: 'my-project-cron-{environment}'

prod:
  alarm:
    enabled: True
    email: prod-alerts@domain.com
  every:
    minutes: 5

staging:
  every:
    minutes: 5

dev:
  enabled: False
```

The settings for each environment will be:

* prod:
  * enabled: True
  * bucket: my-project-cron-prod
  * alarm:
    * enabled: True
    * email: prod-alerts@domain.com
  * every:
    * minutes: 5

* staging:
  * enabled: True
  * bucket: my-project-cron-staging
  * alarm:
    * enabled: False
    * email: ''
  * every:
    * minutes: 5

* dev:
  * enabled: False
  * bucket: my-project-cron-dev
  * alarm:
    * enabled: False
    * email: ''

### Commands

The **LambdaCron** CLI uses the [AWS CLI](https://github.com/aws/aws-cli), and translates
every command into an AWS CLI command.  The AWS account used should be configured for AWS
CLI access.  The LambdaCron CLI allows different AWS CLI
[profiles](http://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html) to
be specified.

The following is the list of commands available.

#### create

Create new **LambdaCron** environment in the AWS account.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--create-bucket**: Flag to indicate that bucket must be created in S3 (optional)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### update

Update new settings for the environment.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### start

Enable LambdaCron to run.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### stop

Disable LambdaCron, and it won't run until it is enabled (#start command) again.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### invoke

Invoke Lambda function cron manually.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### delete

Delete **LambdaCron** environment from the AWS account.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--delete-bucket**: Flag to indicate that the bucket must be deleted from S3 (optional)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

Note: The bucket must be empty before it can be deleted.

#### upload-tasks

Upload tasks to S3 bucket to be run with LambdaCron. It will sync the directory
with S3, including deleting tasks have been deleted from the local directory.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--directory (-d)**: Path to directory that contains tasks definitions (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### validate

Validate a tasks checking if they match with the schema. It can validate a task
from a file or a set of tasks in a directory.

Parameters:

* **--task-file (-t)**: File that contains a task definition.
* **--task-directory (-d)**: Directory with a set of files with taqsks definitions.


## Tasks

Tasks are defined in YAML files, with each task in an independent file. A task must follow
the JSON schema provided in this repo: [schema](./lambda_cron/schema.json).

All tasks must contain the following keys and values:

* **name**: task name
* **expression**: crontab expression
* **task**: task definition (customized for each type of tasks)

Each type of task has its own set of required keys as described in the following section.


### Queue task

It sends a message to an AWS SQS queue.
The task definition must contains following keys:

* **type**: *queue*
* **QueueName**: Name of the queue (string)
* **MessageBody**: Message to be sent (YAML/JSON)

``` yaml
name: 'Send performance report every morning'
expression: '0 9 * * *'
task:
  type: 'queue'
  QueueName: 'my-scheduler-queue'
  MessageBody:
    name: 'Performance report'
    type: 'report'
    sql: 'SELECT ....'
    recipients:
      emails: ....
```

Message is sent using [boto3 SQS.Queue.send_message](http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#SQS.Queue.send_message)
All parameters of the function will be supported soon.

### Lambda task

It invokes an AWS lambda functions.
The task definition must contain the following keys:

* **type**: *lambda*
* **FunctionName**: Name of the Lambda function to invoke (string)
* **InvokeArgs**: arguments to send (YAML/JSON)

``` yaml
name: 'Run ETL process every hour'
expression: '0 * * * *'
task:
  type: 'lambda'
  FunctionName: 'run-etl-process-prod'
  InvokeArgs:
    source: 's3://my-data-source/performance'
    output: 's3://my-data-output/performance'
```

The function is invoked using [boto3 Lambda.Client.invoke_async](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.invoke_async)

### Batch task

It submits AWS Batch jobs.
The task definition must contain the following keys:

* **type**: *batch*
* **jobName**: name to assign to the job (string)
* **jobQueue**: name of the queue in AWS Batch (string)
* **jobDefinition**: name of the job definition in AWS Batch (string)

``` yaml
name: 'Enrich new stats every hour'
expression: '0 * * * *'
task:
  type: 'bath'
  jobName: 'enrich-stats'
  jobDefinition: 'enrich-stats-definition:1'
  jobQueue: 'jobs_high_priority'
```

It is a wrapper for [boto3 Batch.Client.submit_job](http://boto3.readthedocs.io/en/latest/reference/services/batch.html#Batch.Client.submit_job).
All parameters for the method can be set in the task definition.

### HTTP task

It sends an HTTP request (GET or POST).
The task definition must contain the following keys:

* **type**: *http*
* **method**: http method (get | post)
* **request**: YAML with parameters to send for the selected method using [Requests](http://docs.python-requests.org/en/master/)

``` yaml
name: 'helth check every hour'
expression: '0 * * * *'
task:
  type: 'http'
  method: 'get'
  request:
    url: 'http://helthcheck.my-domain.com'
    params:
      service: 'lambda'
```

It is a wrapper over [Requests](http://docs.python-requests.org/en/master/).
All HTTP methods will be supported soon.

## Frequency

#### Execution time
All tasks scheduled to run between the current event and the next event will be run immediately.

Example: LambdaCron runs every hour ('0 * * * *'), tasks '0 1 * * *' and '58 1 * * *' will run at the same time.

####  Task frequency
LambdaCron will execute a task at most once for each invocation.  This can result in a task being run fewer times than it's cron expression implies.

Example: If LambdaCron runs every hour ('0 * * * *'), a task '*/15 * * * *' will only run once an hour.  If LambdaCron runs every minute ('* * * * *'), a task '*/15 * * * *' will only run four times an hour.  You can set up LambdaCron to run more frequently than an hour if you need a task to be run more frequently.

####  Frequecy and Precision

Events are based on [AWS CloudWatch Events](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html).
You can learn about them in the [Scheduled Events documentation](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html):

* "The finest resolution using a Cron expression is a minute"
* "Your scheduled rule is triggered within that minute, but not on the precise 0th second"

Be aware of this.

# Requirements

* Python 2.7
* boto3
* pip
* AWS account
* awscli (configured)

**LambdaCron** is based 100% on AWS cloud.

## Getting Started

**Important!** The tool is not available in **pip** yet. If you want to try it, check [Development](#development)

### Install

``` bash
$ pip install lambda-cron
```

### Usage

Create your first environment (called 'test') with default settings:

``` bash
$ lambda-cron create --environment=test --create-bucket
```

If you want to set some custom settings, create the setting file in the home
directory of the user who is running the tool.

* `~/.lambda-cron.yml`

For help:

``` bash
$ lambda-cron --help
```

or for each command:

``` bash
$ lambda-cron create --help
```

## Development

To start working with **LambdaCron** you should clone the project, create a
virtualenv (optional) and install dependencies:

``` bash
$ git clone https://github.com/MediaMath/lambda-cron.git
$ cd lambda-cron
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements-dev.txt
$ ./lambda_cron/lambda-cron --help
```

## Contributing

Contributions are welcome. You can find open issues with some features and
improvements that would be good to have in **LambdaCron**.

Before contribute we encourage to take a look of following
[tips provided by GitHub](https://guides.github.com/activities/contributing-to-open-source/)
