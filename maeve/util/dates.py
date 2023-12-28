# Week is derived from pandas and starts at zero for any days prior to the first Sunday (week day0)
# ISO uses the week containing the first Thursday of the year as the first week of the year.

# A standard Financial or Fiscal Year (FY) aligns the year end date to the last date of a given qtr,
#  which will be the last date of a month
# FY week 1 starts on first day of FY and changes to wk2 on the first change of week based on day num0. This
# means the first week will be variable in length and is usually short.
# In this type of FY, Period is based on the number of the month from the start of the FY

# A custom FY will align the year end to a specified day, eg a Friday (either last or nearest x day of the year).
# This allows for FY start to align exactly with week start, so weeks will always be 7 days in length
# from year start and only vary in length for the final week of the year.
# This means Periods can be assigned that align with yr and wk start and are allocated by any variation
# of 4-4-5 per 13 week quarter

import pandas as pd
import datetime
from workalendar.registry import registry
from workalendar.registry_tools import iso_register
from itertools import cycle, islice


class Dates:
    def __init__(self,
                 start_date: str,
                 end_date: str,
                 end_day: int = 6,
                 country: str = 'GB',
                 ann_fixed_hols: list[tuple[int, int, str]] = (),
                 ann_var_hols: list[tuple[str, int, int, str]] = (),
                 additional_hols: dict = {},
                 ):

        # Calculate start day from end day
        days = [0, 1, 2, 3, 4, 5, 6]
        start_day = days[end_day - 6]

        self.calendar = self.create_calendar(country,
                                             ann_fixed_hols=ann_fixed_hols,
                                             ann_var_hols=ann_var_hols,
                                             additional_hols=additional_hols,
                                             )
        self.dates = self._create_dates_df(start_date, end_date, start_day, end_day)

    def _create_dates_df(self,
                         start_date: str,
                         end_date: str,
                         start_day: int = 0,
                         end_day: int = 6,
                         ):
        # Start and end should fall on start and end of a quarter and be at least a year

        ts_start = pd.to_datetime(start_date) - pd.to_timedelta(8, unit='d')
        ts_end = pd.to_datetime(end_date) + pd.to_timedelta(8, unit='d')
        ts = pd.date_range(ts_start, ts_end, freq='D')

        ddf = pd.DataFrame(index=ts,
                           data={'Date': ts,
                                 'Year': ts.year,
                                 'Quarter': ts.quarter,
                                 'Month': ts.month,
                                 'Month_Name': ts.month_name(),
                                 'ISOWeek': ts.isocalendar().week,
                                 'Week': ts.strftime('%W').astype('int'),
                                 'Day': ts.dayofweek,
                                 'Day_Name': ts.day_name(),
                                 'Day_In_Month': ts.day,
                                 'Day_Of_Year': ts.dayofyear,
                                 })

        # Set week and quarter start and end dates
        # Pandas dayofweek 0 is Monday
        ddf.loc[ddf.Day == start_day, 'Week_Start_Date'] = ddf.loc[ddf.Day == start_day, 'Date']
        ddf.loc[ddf.Day == end_day, 'Week_End_Date'] = ddf.loc[ddf.Day == end_day, 'Date']
        ddf.loc[ddf[['Year', 'Quarter']].drop_duplicates(keep='first').index, 'Qtr_Start_Date'] = \
            ddf.loc[ddf[['Year', 'Quarter']].drop_duplicates(keep='first').index, 'Date']
        ddf.loc[ddf[['Year', 'Quarter']].drop_duplicates(keep='last').index, 'Qtr_End_Date'] = \
            ddf.loc[ddf[['Year', 'Quarter']].drop_duplicates(keep='last').index, 'Date']

        ddf.Week_Start_Date.ffill(inplace=True)
        ddf.Qtr_Start_Date.ffill(inplace=True)
        ddf.Week_End_Date.bfill(inplace=True)
        ddf.Qtr_End_Date.bfill(inplace=True)

        ddf = ddf.copy().query("@start_date <= Date <= @end_date")
        ddf['Work_Days'] = ddf.apply(lambda x: self.calendar.get_working_days_delta(x.Week_Start_Date,
                                                                                    x.Week_End_Date,
                                                                                    include_start=True),
                                     axis=1)

        return ddf

    def create_calendar(self,
                        country: str = 'GB',
                        ann_fixed_hols: list[tuple[int, int, str]] = (),
                        ann_var_hols: list[tuple[str, int, int, str]] = (),
                        additional_hols: dict = {},
                        ):
        calendar_cls = registry.get(country)

        class Calendar(calendar_cls):

            def __init__(self,
                         ann_fixed_hols: list[tuple[int, int, str]] = (),
                         ann_var_hols: list[tuple[str, int, int, str]] = (),
                         additional_hols: dict = {},
                         **kwargs,
                         ):

                super().__init__(**kwargs)
                self.FIXED_HOLIDAYS = self.FIXED_HOLIDAYS + ann_fixed_hols
                self.additional_holiday_dict = additional_hols

            def additional_holiday(self, year):
                additional = self.additional_holiday_dict.get(year, None)
                return additional

            def get_variable_days(self, year):
                # usual variable days
                days = super().get_variable_days(year)

                for hol in ann_var_hols:
                    func = getattr(self, hol.get('function'))
                    days.append((func(year, *hol.get('args')),
                                 hol.get('label', 'Extra Holiday')))

                additional = self.additional_holiday(year)
                if additional:
                    days.extend(additional)

                return days

        return Calendar(ann_fixed_hols=ann_fixed_hols,
                        ann_var_hols=ann_var_hols,
                        additional_hols=additional_hols)

