[![Build Status](https://travis-ci.com/MediaMath/knox-lambda-cron.svg?token=tMt81cZ8XUGin1RurU5s&branch=master)](https://travis-ci.com/MediaMath/knox-lambda-cron)
# LambdaCron

**LambdaCron** is a serverless cron tool. It provides a way to run scheduled tasks
on AWS cloud and all managed by a command line tool ([LambdaCron CLI](#lambdacron-cli)).

Tasks are scheduled using the same syntax for expressions as well known
linux [crontab](https://help.ubuntu.com/community/CronHowto).

**LambdaCron** offer 3 different type of task to run:

* Queue task: send message to AWS SQS queue.
* Invoke Lambda task: invoke AWS lambda function.
* HTTP task: send HTTP requests (GET & POST).

Tasks are defined in YAML files and are stored on a S3 bucket.

## LambdaCron CLI

**LambdaCron** provide a CLI tool that allow to manage you cron tasks from you localhost,
without needing to access to AWS console.

Also it allows to run multiple environments with different settings. As many environments
as desired can be set up.

### Settings

There are 3 levels of preferences for settings:

* Environment: Custom values for an specific environment.
* Global: Custom values that will have effect to all environments created.
* Default: Default value for options in case no custom values are specified (by environment or globally)

First level of preference is *Environment*, followed by *Global* and finally *Default*. When creating
and environment some settings can be customized by environment, others globally and others with default
values.

Settings are saved in a YAML file. Each environment is defined with a root key the YAML
as the global settings with the key *global*.

Following are the available options:

#### bucket

Name of the bucket where lambda function code will be hosted and tasks stored.

```yaml
bucket: 'my-custom-bucket-name'
```

You can use the pattern **{environment}** in the string for the bucket, it will
be replaced by the environment name.

**Defualt**: lambda-cron-{environment}

The bucket will have to folders:

* code/
* tasks/

#### every (frequency)

Frequency with which the lambda function that evaluate tasks will run.
It indicates the frequency by **minutes OR hours** with an integer number.
It is specified with one of the following parameters:

* minutes
* hours

```yaml
every:
    minutes: 5
```

**Defualt**: every hour.

More info for [frequency](#frequency)

#### alarm

Alarm can be set up using CloudWatch metrics. It use the following parameters:

* enabled
* email (Required if alarm is enabled).

```yaml
alarm:
    enabled: True
    email: my-mailing-list@email.com
```

**Defualt**: not enabled.

#### enabled

It allows to enabled/disabled the cron.

```yaml
enabled: True
```

**Defualt**: enabled.

#### Example

```yaml
global:
  bucket: 'my-project-cron-{environment}'

prod:
  alarm:
    enabled: True
    email: dev-alerts@domain.com
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
    * email: dev-alerts@domain.com
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

* staging:
  * enabled: False
  * bucket: my-project-cron-dev
  * alarm:
    * enabled: False
    * email: ''
  
### Commands

**LambdaCron** CLI use [aws-cli](https://github.com/aws/aws-cli), every command
is translated into aws-cli command. AWS account should be configured for aws-cli. 
LambdaCron CLI allow to specify different aws-cli profiles.

Following is the list of commands available.

#### create

Create new **LambdaCron** environment in the AWS account.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--enabled (-n)**: Enabled or disabled lambda cron (True | False) (optional)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### update

Update new settings for the environment.

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--enabled (-n)**: Enabled or disabled lambda cron (True | False) (optional)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### invoke

Invoke lambda function cron manually

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)

#### delete

Delete **LambdaCron** environment from the AWS account

Parameters:

* **--environment (-e)**: Environment to work with (string)
* **--aws-profile (-a)**: AWS profile to use from aws-cli (string) (optional)


**Important!*: if parameter **--enabled (-n)** is specified it will overwrite 
setting value for **enabled**.














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
    * Improve output
    
enable/disable tasks
manage logs
index file
show sumary
    
    
#### Frequency
 - cada minuto, aws no garantiza el segundo 0.
 - La mayor frequencia de ejcucion es la frequencia con la que se ejecuta la lambda function.
 
#### How it works
Cloudformation stack