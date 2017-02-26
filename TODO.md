
# TODO - LambdaCron

This files content a set of features and/or improvements that would be
good to have in **LambdaCron**

### Disable task
Currently the only way to disable tasks is to remove the file that define
the task. Be able to disable tasks in the task definition could be useful.

Proposals:
1. Add new attribute in task definition to indicate if the task is enabled or disabled:
    * enabaled: [True|False] (True by default)
    
1. Replace cron expression with a keyword, ie. disabled
    
### Tasks Index
When AWS Lambda function run it reads all the task definitions (yml files) in *tasks* and
evaluate the cron expression for each of them. While the number of task grows
performance can be affected negatively. 

Proposal:
1. When uploading the tasks create a file indexing tasks files by cron expression.
In this way the AWS Lambda function will read the index file, evaluate different cron
expressions only once and will read only the files with the tasks that must be executed.
Example:

```yaml
*/30 * * * *:
    - my_task_definition_1.yml
    - my_task_definition_2.yml
0 * * * *:
    - my_task_definiiton_3.yml
```

### Support parameters for [boto3 SQS.Queue.send_message](http://boto3.readthedocs.io/en/latest/reference/services/sqs.html#SQS.Queue.send_message)
For **Queue** tasks, currently, the tool only allow to indicate the message body 
to send to the queue. It doesn't allow the possibility to use all options provided
by the library.

Proposal:
1. Update task runner to handle all or most useful options provided by boto3
to send a message to a SQS queue.

### Support HTTP methods in [Requests](http://docs.python-requests.org/en/master/)
The current version of **LambdaCron** only allow to send **GET** and **POST** requests.

Proposal:
1. Update task runner to handle all (of most of them) HTTP methods available in
[Requests](http://docs.python-requests.org/en/master/)

### Improve CLI output
The CLI output shows the output/results of the commands executed to do the job. It
is not user friendly.

Proposal:
1. Hide output from the commands executed by the tool and show meaningful output
for the user:
    * Summary of the task running (environment and options)
    * Status of the process
    
### Allow nested setting files
Currently **LambdaCron** allows to set environment options in one file
(*~/.lambda-cron.yml*). Could be good to be able to set environment options
in different files (different projects).

Proposal:
1. Be able to include setting files in *~/.lambda-cron.yml*. For example:

```yaml
my-project-a:
    settings: /path/to/my-project-a/lambda-cron.yml
my-project-b:
    settings: /path/to/my-porject-b/lambda-cron.yml
```

### Add additional commands
Continue adding commands to the tool that would allow to do/check anything
with the tool in the command line (as it would be crontab) without having
to access to AWS console.

Proposals:
1. Manage/show logs from CloudWatch in the terminal.
1. Check status of the project in the terminal: enabled/disabled, number of tasks, ...
