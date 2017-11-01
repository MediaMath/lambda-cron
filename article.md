# LambdaCron - MediaMath's Financial Platform

MediaMath&#39;s Financial Platform team (FINP) is responsible for building a scalable, stable and secure platform for management of all internal financial data. We serve as the authoritative source of record and support all financial processes (e.g., billing, forecasting, compensation, auditing, etc.) and provide internal clients with access in support of their reporting and analysis needs.

In the last year, the FINP has been renovating its infrastructure moving to a service oriented architecture and joining the trend of serverless architecture. In our thinking, using a serverless architecture allows for the team to reduce daily operations and spend more time in business-related work.

One of the first services that was brought to life in this process of renovation was a service that allowed the FINP to run asynchronous queries on a PostgreSQL database, in a safe manner, and save results in S3 and/or send them by email. It was called Preakness. One of the key responsibilities of the FINP is to provide financial reports to team&#39;s clients (internal and external), Preakness was an ideal partner to run and send some of those reports. However most of the reports had to run periodically, so we had to find a way to schedule reports running on Preakness and, in general, schedule Preakness jobs.

## **Potential Solutions**

### **1. Crontab**

The most simple and straightforward way to schedule task is using Linux  [crontab](https://help.ubuntu.com/community/CronHowto), with crontab we could schedule scripts to run periodically and trigger Preakness&#39; jobs. It was simple and feasible but not an option the team was seriously considering: running an instance exclusively to run crontab and trigger the jobs didn&#39;t make sense to us. We could re-use or share resources with other services but it hardly would fit in a service oriented architecture and not close at all to a servessless architecture.

### **2. AWS CloudWatch Events**

AWS configures events using  [CloudWatch](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html), to invoke other AWS services in a cron-like way. As the team&#39;s infrastructure is based on AWS, using AWS services to schedule events made total sense. Preakness also uses Simple Queue Service (SQS) to queue jobs integrated with CloudWatch events. It seemed like a good option, however we found some negative aspects we didn&#39;t feel comfortable with:

- The service itself has some serious  [limitations](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/cloudwatch_limits_cwe.html).
- Events are attached to AWS services and depend on AWS releases.
- It is very different from the traditional way to manage and run cron jobs, not user-friendly.
- Changes in your events imply changes in your AWS infrastructure.

### **3. Custom solution**

The third option was to build an in-house solution that satisfies some requisites as:

- Easy and friendly way to schedule jobs: it should allow users (including non-developers) to define and schedule jobs.
- Reduce maintainability of the service as much as possible: Serverless.

We decided to go for the third option. The simple service allowed us to schedule messages to SQS queues by writing few lines in a YAML file. As we were trying to find a solution to schedule jobs for Preakness we realized the potential it had:

- What if it were able to trigger different types of events?
- Could it be detached from FINP architecture?

That was how LambdaCron was born.

LambdaCron is a serverless cron tool. It provides an easy way to run scheduled tasks on the AWS cloud, defined in YAML, managed by a command line tool and using the same syntax for expressions as Linux  [crontab](https://help.ubuntu.com/community/CronHowto). LambdaCron fills in the gap by providing a way to manage Serverless cron jobs just like cron. With LambdaCron you define each of your tasks in an independent YAML file.

LambdaCron offers five different types of tasks:

- **Queue task** : send a message to AWS SQS queue.
- **Lambda task** : invoke AWS Lambda function.
- **Batch task** : submit AWS Batch job.
- **Athena task** : submit AWS Athena queries.
- **HTTP task** : send HTTP requests (GET &amp; POST).

It is integrated with four AWS services and HTTP requests. LamdaCron is easily integrated with other services and it is ready to reach any service available by an API.

The tool is production ready but it still has a long way to go. It satisfies the needs of MediaMath&#39;s Financial Platform but there is room to increase functionality and improve. The three main lines where we feel it must improve are:

- **Tasks** : cover all options in current type of tasks and continue adding new types.
- **CLI** : improve and continue adding functionality to the CLI. Tasks should be totally managed from the command line and without login in the AWS console.
- **Templates** : use a templating system to define tasks and be able to include variables in the definition.

## **Use Case**

MediaMath&#39;s Financial Platform is really into AWS and loves trying new services. We have been using  [AWS Batch](https://aws.amazon.com/batch/) since the release date. But we found it was not possible to schedule AWS Batch jobs directly from the service. One of the simplest ways to schedule AWS Batch jobs is to write a lambda function to trigger a job to schedule the lambda function. It is easy but it implies more code and more infrastructure to maintain.

Here&#39;s an example of how to use LambdaCron to trigger an AWS Batch job. This is an AWS Batch job definition used by FINP to run reports:

```json
{
    "jobDefinitionName": "vendor-reports-prod",
    "type": "container",
    "containerProperties": {
        "image": "438025690015.dkr.ecr.us-east-1.amazonaws.com/db-refresh:prod",
        "jobRoleArn": "arn:aws:iam::438025690015:role/db-refresh-prod-role",
        "vcpus": 1,
        "memory": 512,
        "environment": [
            {
                "name": "CATEGORY",
                "value": "prod"
            },
            {
                "name": "AWS_DEFAULT_REGION",
                "value": "us-east-1"
            }
        ],
        "command": [
            "./vendor_reports/vendor-reports.py",
            "Ref::period",
            "Ref::report_type",
            "--queue-name=preakness-prod"
        ]
    }
}
```

This job is used to run weekly and monthly reports so we want to schedule this job to run weekly and/or monthly. A container is running a python program which receives three arguments, two of those arguments (Ref::period, Ref::report\_type) are parameters that must be passed when submitting the job.

This is a LambdaCron task definition to run the monthly report:

```yaml
name: vendor_reports_monthly
expression: '0 17 5 * *'
task:
  type: 'batch'
  jobName: 'vendor-reports-prod-monthly'
  jobQueue: 'dc-batch-queue-low-prod'
  jobDefinition: 'vendor-reports-prod'
  parameters:
    report_type: '--monthly'
    period: '--last-month'
```


The job is scheduled to run at 5 pm on the fifth of every month. The  **type**  of the task is specified inside the key  **task,** along with parameters required by AWS Batch API to submit a job. After defining the task, it is uploaded to LambdaCron using LambdaCron CLI.

Before creating tasks, a LambdaCron environment must be deployed by following the instructions in the  [README](https://github.com/mediaMath/lambda-cron) of the project.

LambdaCron CLI also provides commands that can automate development and maintenance tasks. For example, validate and upload tasks to a LambdaCron environment using Continuous Integration tools. We will follow up with more examples and how to work with LambdaCron in future blog posts.

Any service accessible by an API (including non AWS services) can be reached by LambdaCron so you don&#39;t have to rely on additional services features to schedule your tasks and/or write extra code.
