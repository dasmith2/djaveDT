from datetime import datetime, date, time
import unittest

import pytz

from djavedt import (
    now, PastMonth, past_x_months, years_old, str_to_tz_dt, time_str_to_time)


class NowTests(unittest.TestCase):
  def test_now(self):

    def use_django_now():
      # Early in the morning UTC time January 2nd.
      return pytz.timezone('UTC').localize(datetime(2020, 1, 2, 1, 0, 0, 0))

    new_york_tz = pytz.timezone('America/New_York')
    self.assertEqual(
        # Late in the evening NY time January 1st
        new_york_tz.localize(datetime(2020, 1, 1, 20, 0, 0, 0)),
        now(use_django_now=use_django_now, tz_str='America/New_York'))


class Past12MonthsTests(unittest.TestCase):
  def test_past_x_months(self):
    expected = [
        PastMonth(year=2019, month=8, months_ago=0),
        PastMonth(year=2019, month=7, months_ago=1),
        PastMonth(year=2019, month=6, months_ago=2),
        PastMonth(year=2019, month=5, months_ago=3),
        PastMonth(year=2019, month=4, months_ago=4),
        PastMonth(year=2019, month=3, months_ago=5),
        PastMonth(year=2019, month=2, months_ago=6),
        PastMonth(year=2019, month=1, months_ago=7),
        PastMonth(year=2018, month=12, months_ago=8),
        PastMonth(year=2018, month=11, months_ago=9),
        PastMonth(year=2018, month=10, months_ago=10),
        PastMonth(year=2018, month=9, months_ago=11)]
    got = list(past_x_months(12, nnow=str_to_tz_dt('2019-08-28 14:46')))
    self.assertEqual(expected, got)


class YearsOldTests(unittest.TestCase):
  def test_years_old(self):
    self.assertEqual(None, years_old(None))
    self.assertEqual(0, years_old(
        date(2018, 1, 1), nnow=str_to_tz_dt('2018-01-01')))
    self.assertEqual(0, years_old(
        date(2018, 1, 1), nnow=str_to_tz_dt('2018-01-02')))
    self.assertEqual(0, years_old(
        date(2018, 12, 2), nnow=str_to_tz_dt('2019-12-01')))
    self.assertEqual(1, years_old(
        date(2018, 12, 2), nnow=str_to_tz_dt('2019-12-02')))
    self.assertEqual(1, years_old(
        date(2018, 12, 2), nnow=str_to_tz_dt('2020-12-01')))


class TimeStrToTimeTests(unittest.TestCase):
  def test_time_str_to_time(self):
    self.assertEqual(time(0, 0), time_str_to_time('00:00'))
    self.assertEqual(time(0, 0), time_str_to_time('12:00 AM'))
    self.assertEqual(time(11, 59), time_str_to_time('11:59'))
    self.assertEqual(time(11, 59), time_str_to_time('11:59 AM'))
    self.assertEqual(time(12, 0), time_str_to_time('12:00'))
    self.assertEqual(time(12, 0), time_str_to_time('12:00 PM'))
    self.assertEqual(time(23, 59), time_str_to_time('11:59 PM'))
    self.assertEqual(None, time_str_to_time(None))


if __name__ == '__main__':
  unittest.main()
