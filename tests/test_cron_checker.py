from lambda_cron.aws.lib.cron_checker import CronChecker


def test_should_run_basic():
    cron_checker = CronChecker('2016-10-01T09:00:00Z')
    assert cron_checker.should_run('0 9 * * *') == True


def test_should_not_run_basic():
    cron_checker = CronChecker('2016-10-01T09:00:00Z')
    assert cron_checker.should_run('0 10 * * *') == False


def test_period_1_hour_should_run_min_30():
    cron_checker = CronChecker('2016-10-01T09:00:00Z')
    assert cron_checker.should_run('30 9 * * *') == True


def test_period_30_min_should_not_run_min_30():
    cron_checker = CronChecker('2016-10-01T09:00:00Z', 0, 30)
    assert cron_checker.should_run('30 9 * * *') == False


def test_period_5_min_should_run_min_04():
    cron_checker = CronChecker('2016-10-01T09:00:00Z', 0, 5)
    assert cron_checker.should_run('4 9 * * *') == True


def test_period_5_min_should_not_run_min_05():
    cron_checker = CronChecker('2016-10-01T09:00:00Z', 0, 5)
    assert cron_checker.should_run('5 9 * * *') == False


def test_period_5_min_should_run_before_the_time_less_than_5_minutes():
    cron_checker = CronChecker('2016-10-01T08:58:59Z', 0, 5)
    assert cron_checker.should_run('0 9 * * *') == True


def test_period_5_min_should_not_run_before_the_time_more_or_equal_5_minutes():
    cron_checker = CronChecker('2016-10-01T08:55:59Z', 0, 5)
    assert cron_checker.should_run('0 9 * * *') == False


def test_period_2_hours_should_run_for_less_2_hours_ahead_process():
    cron_checker = CronChecker('2016-10-01T08:55:59Z', 2, 0)
    assert cron_checker.should_run('0 10 * * *') == True


def test_period_2_hours_should_run_for_less_2_hours_ahead_process_II():
    cron_checker = CronChecker('2016-10-01T08:55:59Z', 2, 0)
    assert cron_checker.should_run('54 10 * * *') == True


def test_period_2_hours_should_not_run_for_more_than_2_hours_ahead_process():
    cron_checker = CronChecker('2016-10-01T08:55:59Z', 2, 0)
    assert cron_checker.should_run('56 10 * * *') == False
