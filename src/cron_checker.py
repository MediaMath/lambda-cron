from croniter import croniter
from datetime import datetime, timedelta


class CronChecker:

    def __init__(self, current_timestamp, hour_period=1, minutes_period=0):
        self.start_of_period = self.get_start_of_period(current_timestamp)
        self.period = timedelta(hours=hour_period, minutes=minutes_period)

    def get_start_of_period(self, timestamp):
        """ Find the start of the current period
        Arguments:
        timestamp - ISO 8601 stamp string

        Retruns:
        Datetime objects for 1 second the start current evaluation period
        """
        actual_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        ideal_time = actual_time.replace(second=0)
        before_period = ideal_time - timedelta(seconds=1)
        return before_period

    def should_run(self, cron_expression):
        next_event = croniter(cron_expression, self.start_of_period).get_next(datetime)
        return self.start_of_period < next_event <= (self.start_of_period + self.period)
