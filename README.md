[![Build Status](https://travis-ci.com/MediaMath/knox-lambda-cron.svg?token=tMt81cZ8XUGin1RurU5s&branch=master)](https://travis-ci.com/MediaMath/knox-lambda-cron)

![diagram](/diagram.png)

## Local Setup

### Requirements
- Python 2.7
- Virtual Environment
- pip
- Boto3
  - Boto3 is installed as part of the lambda functions Environment.  To aviod the overhead of including it in your deployment artifact install boto3 on your system instead of in the virtual environment
- awscli (configured)

### Setup
From the repo root dir
``` bash
$ virtualenv venv
$ pip install -r requirements.txt
```


## Sample Task Definition

``` yaml
name: sample name
expression: "0 2 * * *"
queue_name: some-sqs-queue
task:
  key1: value 1
  key2: value 2
```


### Diagram
The diagram was created with draw.io, using the lambda-cron.xml file in this repo
