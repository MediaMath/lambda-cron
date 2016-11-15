import json


class TaskRunner:
    def __init__(self, cron_checker, queue):
        self.cron_checker = cron_checker
        self.queue = queue

    def run(self, task_definition):
        if self.cron_checker.should_run(task_definition['expression']):
            self.queue.send_message(MessageBody=json.dumps(task_definition['message']))
            return True
        return False
