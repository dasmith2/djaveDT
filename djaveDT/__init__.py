from collections import namedtuple

from datetime import datetime, date, timedelta, time
import math
import pytz
import re

from django.conf import settings
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import make_aware, is_aware, now as django_now


def tz_dt_to_str(tz_dt, tz_str=None):
  """ Turn tz_dt into a human readable string. For example, Jan. 10, 2019, 8:18
  a.m.  I just reverse engineered Django's formula for turning datetimes into
  readable strings. """
  # I do it this way because if you do def tz_dt_to_str(tz_dt,
  # tz_str=settings.TIME_ZONE) the tests would require a full blown Django
  # instance.
  tz_str = tz_str or settings.TIME_ZONE
  tz_dt = tz_dt_to_tz_dt(tz_dt, tz_str)
  return dt_to_str(tz_dt)


def d_to_str(d):
  # I don't do '%b. %d, %Y' because "May. 5, 2020" looks dumb.
  return d.strftime('%b %d, %Y')


def dt_to_str(tz_dt):
  return ''.join([dt_to_date_str(tz_dt), ', ', dt_to_time_str(tz_dt)])


def dt_to_d_str(tz_dt, tz_str=None):
  return d_to_str(tz_dt_to_tz_dt(tz_dt, tz_str=tz_str))


def dt_to_date_str(tz_dt):
  return d_to_str(tz_dt.date())


def dt_to_time_str(tz_dt, tz_str=None):
  return time_to_time_str(tz_dt_to_tz_dt(tz_dt, tz_str=tz_str).time())


def time_to_time_str(t):
  join_me = []
  minute_str = ''
  if t.minute > 0:
    if t.minute >= 10:
      minute_str = ':{}'.format(t.minute)
    else:
      minute_str = ':0{}'.format(t.minute)
  if t.hour < 12:
    join_me.extend([str(t.hour), minute_str, ' a.m.'])
  elif t.hour == 12:
    if t.minute == 0:
      join_me.append('noon')
    else:
      join_me.extend([str(t.hour), minute_str, ' p.m.'])
  else:
    join_me.extend([str(t.hour - 12), minute_str, ' p.m.'])
  return ''.join(join_me)


def tz_dt_to_abbr_str(tz_dt, tz_str=None):
  tz_str = tz_str or settings.TIME_ZONE
  return tz_dt_to_tz_dt(tz_dt, tz_str).strftime('%Y-%m-%d %H:%M EST')


def parse_dt(dt_maybe):
  """ This is mainly useful for tests where you wanna do stuff like
  my_test_dt = parse_dt('2018-05-15 16:00') and have it be made tz aware.
  dt_maybe can be a date, a datetime, or a string representing either
  a date or a datetime. It may be tz aware or not. This function will
  then return a timezone aware datetime. """
  d_or_dt = None
  if dt_maybe.__class__ is str:
    d_or_dt = parse_datetime(dt_maybe) or parse_date(dt_maybe)
  elif dt_maybe.__class__ is datetime or dt_maybe.__class__ is date:
    d_or_dt = dt_maybe
  if not d_or_dt:
    raise Exception('No idea how to get a datetime from {}'.format(dt_maybe))

  if d_or_dt.__class__ is datetime:
    dt_definitely = d_or_dt
  elif d_or_dt.__class__ is date:
    dt_definitely = datetime(d_or_dt.year, d_or_dt.month, d_or_dt.day)
  if is_aware(dt_definitely):
    return dt_definitely
  return make_aware(dt_definitely)


def str_to_dt(dt_str):
  """ If the string contains timezone information, this will return a timezone
  aware datetime. """
  parsed_as_dt = parse_datetime(dt_str)
  if parsed_as_dt:
    return parsed_as_dt
  parsed_as_d = parse_date(dt_str)
  if parsed_as_d:
    return datetime(parsed_as_d.year, parsed_as_d.month, parsed_as_d.day)
  raise Exception('Unable to parse date string {}'.format(dt_str))


def to_d(d_or_d_str):
  """ d_or_d_str can be None, a string like '2012-02-21' or a date. """
  if d_or_d_str is None:
    return None
  if isinstance(d_or_d_str, str):
    return parse_date(d_or_d_str)
  if isinstance(d_or_d_str, date):
    return d_or_d_str
  raise Exception(
      'Im not sure what to do with a {}'.format(d_or_d_str.__class__))


def to_tz_dt(dt_or_dt_str, tz_str=None):
  """ dt_or_dt_str can be None, a string like "2012-02-21 10:28:45", or a
  timezone enabled datetime. This returns in the tz_str timezone if provided,
  otherwise it uses settings.TIME_ZONE """
  if dt_or_dt_str is None:
    return None
  if isinstance(dt_or_dt_str, str):
    return str_to_tz_dt(dt_or_dt_str, tz_str=tz_str)
  elif isinstance(dt_or_dt_str, datetime):
    return tz_dt_to_tz_dt(dt_or_dt_str)
  raise Exception('I am not sure what to do with a {}'.format(
      dt_or_dt_str.__class__))


def str_to_tz_dt(dt_str, tz_str=None):
  """ dt_str is, like, "2012-02-21 10:28:45" while tz_str is, like,
  "Europe/Helsinki". See pytz.all_timezones. This function returns
  something like datetime.datetime(
      2012, 2, 21, 10, 28, 45,
      tzinfo=<DstTzInfo 'Europe/Helsinki' EET+2:00:00 STD>)
  dt_str can also be, like, "2012-02-21" which will just do midnight. """
  if not isinstance(dt_str, str):
    raise Exception(
        'str_to_tz_dt expects a string, not a {}'.format(dt_str.__class__))
  dt = str_to_dt(dt_str)
  if dt.tzinfo:
    if not tz_str:
      return dt
    return tz_dt_to_tz_dt(dt, tz_str=tz_str)
  tz_str = tz_str or settings.TIME_ZONE
  return naive_dt_to_tz_dt(dt, tz_str)


def d_to_naive_dt(d):
  return datetime(d.year, d.month, d.day)


def naive_dt_to_tz_dt(naive, tz_str=None):
  # If you hand this thing noon it'll return noon in New York or whatever. I
  # THINK is_dst is is daylight savings time and is only used in weird corner
  # cases.
  tz_str = tz_str or settings.TIME_ZONE
  return pytz.timezone(tz_str).localize(naive, is_dst=None)


def beginning_of_day(d, tz_str=None):
  """ Given a plain old date, this will return the beginning of that day in
  New York time or whatever. """
  return naive_dt_to_tz_dt(d_to_naive_dt(d), tz_str=tz_str)


def end_of_day(d, tz_str=None):
  return beginning_of_day(d, tz_str=tz_str) + timedelta(days=1)


def tz_dt_to_tz_dt(tz_dt, tz_str=None):
  """ Take a timezone aware datetime that's localized to UTC (or whatever,
  but Django stores and loads datetimes in the database in UTC so that's
  pretty much the use case). Let's say tz_dt is noon on Friday UTC. Let's
  say tz_str is US/Eastern. This should return, like, 8am Friday US/Eastern
  because US/Eastern is 4 timezones behind UTC. We need this because if you
  do my_dt.replace(hour=9), it'll do UTC 9am if my_dt is still in UTC, but
  that might be in the middle of the night if what you wanted to do was
  send something at 9am in Hawaii or whatever. """
  tz_str = tz_str or settings.TIME_ZONE
  return tz_dt.astimezone(pytz.timezone(tz_str))


def dt_for_json(tz_dt, tz_str=None):
  """ If tz_dt is None, return None. Otherwise, put tz_dt in the specified
  timezone. If no timezone is specified, use settings.TIME_ZONE (which for me
  is 'America/New_York'). Return the isoformat. So for instance this could
  return '2020-01-01T13:00:00-05:00' """
  if not tz_dt:
    return None
  if not isinstance(tz_dt, datetime):
    raise Exception((
        'dt_for_json expects a timezone enabled datetime, '
        'not a {}').format(tz_dt.__class__))
  return tz_dt_to_tz_dt(tz_dt).isoformat()


def d_for_json(d):
  if not d:
    return None
  if not isinstance(d, date):
    raise Exception('d_for_json expects a date, not a {}'.format(d.__class__))
  return d.isoformat()


def now(use_django_now=django_now, tz_str=None):
  # django_now is in UTC, so things like now().date() can return tomorrow if
  # you call it past 7pm. use_django_now is there so I can write tests without
  # requiring Django.
  tz_str = tz_str or settings.TIME_ZONE
  return tz_dt_to_tz_dt(use_django_now(), tz_str)


def default_tzinfo(tz_str=None):
  tz_str = tz_str or settings.TIME_ZONE
  return pytz.timezone(tz_str)


def midnight_from_date(date_, tzinfo=None):
  tzinfo = tzinfo or default_tzinfo()
  return tzinfo.localize(datetime(
      year=date_.year, month=date_.month, day=date_.day))


def morning_from_date(date_, tzinfo=None):
  tzinfo = tzinfo or default_tzinfo()
  return tzinfo.localize(datetime(
      year=date_.year, month=date_.month, day=date_.day, hour=11))


def afternoon_from_date(date_, tzinfo=None):
  tzinfo = tzinfo or default_tzinfo()
  return tzinfo.localize(datetime(
      year=date_.year, month=date_.month, day=date_.day, hour=16))


def time_of_day_from_date(date_, hour, tzinfo=None):
  tzinfo = tzinfo or default_tzinfo()
  return tzinfo.localize(datetime(
      year=date_.year, month=date_.month, day=date_.day, hour=hour))


def closest_previous_sunday(date_):
  # Monday == 0, Sunday == 6
  if date_.weekday() == 6:
    return date_
  return date_ - timedelta(days=date_.weekday() + 1)


def closest_previous_first_of_the_month(date_):
  return date_.replace(day=1)


def closest_upcoming_first_of_the_month(date_):
  if date_.day == 1:
    return date_
  if date_.month == 12:
    return date(date_.year + 1, 1, 1)
  return date(date_.year, date_.month + 1, 1)


def tz_dt(year, month, day, hour, tzinfo=None):
  tzinfo = tzinfo or default_tzinfo()
  return tzinfo.localize(datetime(year=year, month=month, day=day, hour=hour))


def ts_to_utc_dt(time_stamp):
  """ Why utcfromtimestamp doesn't return a dt with the utc timezone is
  beyond me. """
  return datetime.utcfromtimestamp(time_stamp).replace(tzinfo=pytz.utc)


def add_months(daate, months):
  to_year = daate.year
  to_month = daate.month + months
  while to_month > 12:
    to_month -= 12
    to_year += 1
  while to_month < 1:
    to_month += 12
    to_year -= 1
  return date(to_year, to_month, daate.day)


def get_readable_duration(ttimedelta):
  parts = []
  days = ttimedelta.days
  if days > 0:
    parts.append(str(days))
    if days == 1:
      parts.append('day')
    else:
      parts.append('days')
  total_seconds = ttimedelta.seconds
  if total_seconds == 0:
    return '0 seconds'
  hours = math.floor(total_seconds / 3600)
  minutes = round((total_seconds % 3600) / 60)
  seconds = total_seconds % 60
  if hours > 0:
    parts.append(str(hours))
    parts.append('hour' if hours == 1 else 'hours')
  if minutes > 0:
    parts.append(str(minutes))
    parts.append('minute' if minutes == 1 else 'minutes')
  if seconds > 0:
    parts.append(str(seconds))
    parts.append('second' if seconds == 1 else 'seconds')
  return ' '.join(parts)


def describe_timedelta(delta):
  hours, remainder = divmod(delta.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return '{:02}:{:02}'.format(int(hours), int(minutes))


PastMonth = namedtuple('PastMonth', 'year month months_ago')


def past_x_months(x, nnow=None):
  """ Including the 1st of nnow's month """
  if nnow is None:
    nnow_date = date.today()
  elif isinstance(nnow, date):
    nnow_date = nnow
  elif isinstance(nnow, datetime):
    nnow_date = nnow.date()
  else:
    raise Exception(nnow)
  this_month = nnow_date.month
  this_year = nnow_date.year
  for i in range(12):
    next_month = (this_month - 1 - i) % 12 + 1
    next_year = this_year
    if i >= this_month:
      next_year -= 1
    yield PastMonth(next_year, next_month, i)


def years_old(birthdate, nnow=None):
  nnow = nnow or now()
  if not birthdate:
    return None
  today = nnow.date()
  year_delta = today.year - birthdate.year
  if today.month < birthdate.month or (
      today.month == birthdate.month and today.day < birthdate.day):
    return year_delta - 1
  return year_delta


def days_ago_str(day):
  start = ''
  middle = day.strftime('%A, %B %d')  # Monday, January 17
  end = ''
  if day == date.today():
    start = 'Today, '
  elif day == date.today() - timedelta(days=1):
    start = 'Yesterday, '
  elif day == date.today() + timedelta(days=1):
    start = 'Tomorrow, '
  elif day < date.today():
    days_ago = (date.today() - day).days
    end = ', {} days ago'.format(days_ago)
  elif day > date.today():
    days_until = (day - date.today()).days
    end = ', {} days from now'.format(days_until)
  return '{}{}{}'.format(start, middle, end)


def time_str_to_time(time_str):
  """ time_str can be either, like, '17:00' or '05:00 PM' """
  if time_str:
    if re.compile(r'^\d+:\d+$').match(time_str):  # '17:00'
      parts = list(int(p) for p in time_str.split(':'))  # (17, 0)
      return time(*parts)
    found = re.compile(r'(\d+):(\d+) (AM|PM)').match(time_str)  # '05:00 PM'
    if found:
      (hour, minute, am_pm) = found.groups()
      hour = int(hour)
      minute = int(minute)
      # Wikipedia says 11:59 PM means 1 minute before midnight but 12:00 PM
      # means noon and 12:00 AM means midnight.
      if hour == 12:
        if am_pm == 'AM':
          hour -= 12
      elif am_pm == 'PM':
        hour += 12
      return time(hour, minute)
