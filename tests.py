from datetime import datetime
import unittest

import pytz

from djavedt import now


class Tests(unittest.TestCase):
  def test_now(self):

    def use_django_now():
      # Early in the morning UTC time January 2nd.
      return pytz.timezone('UTC').localize(datetime(2020, 1, 2, 1, 0, 0, 0))

    new_york_tz = pytz.timezone('America/New_York')
    self.assertEqual(
        # Late in the evening NY time January 1st
        new_york_tz.localize(datetime(2020, 1, 1, 20, 0, 0, 0)),
        now(use_django_now=use_django_now, tz_str='America/New_York'))


if __name__ == '__main__':
  unittest.main()
