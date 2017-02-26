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
