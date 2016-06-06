from datetime import datetime, timedelta


class BusinessDatetime(object):

    def __init__(self, dt, working_hours=(8.5, 17), working_days=(0, 1, 2, 3, 4), calendar=None):
        self._dt = dt  # self.calc_next_business_day(dt)
        self._calendar = calendar
        self.working_hours = self._start_working_hour, self._end_working_hour = working_hours
        self.start_working_hour, self.start_working_minute = divmod(self._start_working_hour * 60, 60)
        self.start_working_hour = int(self.start_working_hour)
        self.start_working_minute = int(self.start_working_minute)
        self.end_working_hour, self.end_working_minute = divmod(self._end_working_hour * 60, 60)
        self.end_working_hour = int(self.end_working_hour)
        self.end_working_minute = int(self.end_working_minute)
        self.working_days = working_days

        # The end of the current working day supplied by the dt param
        self.current_work_day_end = datetime(dt.year, dt.month, dt.day, self.end_working_hour, self.end_working_minute)

        # The beginning of the current working day supplied by the dt param
        self.current_work_day_start = datetime(dt.year, dt.month, dt.day, self.start_working_hour, self.start_working_minute)

    def __str__(self):
        return self.business_datetime.strftime('%Y-%m-%d %H:%M:%S %z')

    def __sub__(self, other):
        return BusinessDatetime(self.business_datetime - other)

    def __add__(self, other):
        return BusinessDatetime(self.business_datetime + other)

    def out_of_bounds(self, dt):
        return dt > self.current_work_day_end or dt < self.current_work_day_start

    @property
    def business_datetime(self):
        if self._dt.minute >= self.end_working_minute and self._dt.hour >= self.end_working_hour:
            return self.rollforward()
        elif self._dt.minute < self.start_working_minute and self._dt.hour <= self.start_working_hour:
            return self.rollback()
        else:
            return self._dt

    @property
    def next_business_day_start(self):
        """
        datetime object representing the next business days start time.
        :rtype: datetime
        :return:
        """
        d = datetime(self._dt.year, self._dt.month, self._dt.day, self.start_working_hour, self.start_working_minute) + timedelta(days=1)
        while d.weekday() not in self.working_days:
            d += timedelta(days=1)
        return d

    @property
    def previous_business_day_end(self):
        """
        datetime object representing the previous business days end time.
        :rtype: datetime
        :return:
        """
        d = datetime(self._dt.year, self._dt.month, self._dt.day, self.end_working_hour, self.end_working_minute) - timedelta(days=1)
        while d.weekday() not in self.working_days:
            d -= timedelta(days=1)
        return d

    def rollforward(self):
        """
        Return a datetime object which falls within working hours with the starting offset equal to the amount
        of time that the original datetime object exceeds the end working hour.

        ex.
            >>> # The following datetime exceeds the working day by 30 seconds.
            >>> example_dt = datetime(2016, 6, 5, 17, 0, 30)  # 2016-06-05 5:00:30 PM
            >>> example_bdt = BusinessDatetime(example_dt)
            >>> print example_bdt.rollforward()
            2016-06-06 8:30:30
        :return:
        """
        overflow = datetime(self._dt.year, self._dt.month, self._dt.day, self.end_working_hour, self.end_working_minute)
        td = self._dt - overflow
        return self.next_business_day_start + td

    def rollback(self):
        """
        Return a datetime object which falls within working hours with the ending offset equal to the amount
        of time that the original datetime object falls short of the start working hour.

        ex.
            >>> # The following datetime preceeds the working day by 1 minute.
            >>> example_dt = datetime(2016, 06, 05, 8, 29)  # 2016-06-05 8:29:00 AM
            >>> example_bdt = BusinessDatetime(example_dt)
            >>> print example_bdt.rollback()
            2016-06-04 16:59:00
        :return:
        """
        underflow = datetime(self._dt.year, self._dt.month, self._dt.day, self.start_working_hour, self.start_working_minute)
        td = underflow - self._dt
        return self.previous_business_day_end - td


d = datetime.now()
bdt = BusinessDatetime(d)
print bdt

d = datetime(2016, 06, 06, 8, 29, 00)
bdt = BusinessDatetime(d)
print bdt + timedelta(seconds=61)
