# Introduction

These utility functions are helpful in handling dates, datetimes, and timezones
in Django.

# Examples

Let's say you have the following in your Django settings.py

    TIME_ZONE = 'America/New_York'
    USE_TZ = True

Now let's attempt to write our own tomorrow() function.

    from datetime import timedelta
    from django.utils.timezone import now

    def tomorrow():
      # Subtle bug! Django's now() function returns a timezone enabled datetime
      # in UTC, regardless of the TIME_ZONE setting. If it's 11 Wednesday
      # MORNING in New York, this function will work. But if it's 11 Wednesday
      # NIGHT in New York, the UTC timezone is already in Thursday, so in that
      # case this code will return Friday.
      return now().date() + timedelta(days=1)

Here's one way to fix the problem.

    from datetime import timedelta
    from djavedt import now

    def tomorrow():
      # djavedt's now() function returns a timezone enabled datetime in the
      # timezone of the TIME_ZONE setting, which is America/New_York in our example.
      # So this function will work as expected at 11PM in New York.
      return now().date() + timedelta(days=1)
