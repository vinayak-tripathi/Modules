import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ExpiryCalculator:
    def __init__(self, year, holidays, expiry_day_name="Thursday"):
        self.year = year
        self.holidays = holidays
        self.expiry_day_name = expiry_day_name.capitalize()

    @staticmethod
    def _weekday_to_number(weekday: str) -> int:
        """Convert weekday name to its corresponding number (Monday = 0, Sunday = 6)."""
        weekday = weekday.capitalize()

        weekdays_long = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }

        weekdays_short = {
            "Mon": 0,
            "Tue": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6
        }

        if weekday in weekdays_long:
            return weekdays_long[weekday]
        elif weekday in weekdays_short:
            return weekdays_short[weekday]
        else:
            raise ValueError("Invalid weekday name")

    def get_all_weekdays_in_month(self, month: int, year: int):
        """Returns all the dates for the given weekday in a given month of a year."""
        first_day = pd.Timestamp(year=year, month=month, day=1)
        target_weekday = self._weekday_to_number(self.expiry_day_name)
        
        # Find the first occurrence of the target weekday
        first_weekday = first_day + pd.DateOffset(days=(target_weekday - first_day.weekday()) % 7)
        
        # Generate all occurrences of the weekday in the month
        all_weekdays = pd.date_range(first_weekday, pd.Timestamp(year=year, month=month, day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1), freq='7D')
        
        return all_weekdays

    def get_trading_day_before(self, date):
        """Returns the last trading day before or on the given date."""
        while date in self.holidays or date.weekday() >= 5:  # Skip weekends and holidays
            date -= pd.DateOffset(days=1)
        return date
    
    # Worked on v2 or the Expiry calculator as there was a bug in the code. The code failed for the 
    # case 24Apr2025, 30Apr2025. Since 1stMay is holiday and is also first weekly expiry we need to consider
    # 30Apr2025 as 1W expiry for the May Series and 24Apr2025 as Monthly expiry for Apr Series. But the
    # code returned it as monthly expiry and the 24 Apr as 4W Expiry for Apr series. So fixed this here
    def get_all_expiry_dates(self):
        """Generate weekly and monthly expiry dates for Calls, handling holidays."""

        years = self.year
        if isinstance(self.year, int):
            years = [self.year]
        elif not isinstance(self.year, list):
            raise ValueError("Years must be an integer or a list of integers.")
        weekly_expiry_dates = {}
        monthly_expiry_dates = {}
        for year in years:
            for month in range(1, 13):
            # Get all the expiry days for the given weekday in the month
                all_expiry_days = self.get_all_weekdays_in_month(month, year)
                
                # Adjust each weekly expiry date for holidays

                adjusted_weekly_expiries = [self.get_trading_day_before(day) for day in all_expiry_days]
                monthly_expiry_dates[adjusted_weekly_expiries[-1]] = month
                weekly_expiry_dates = weekly_expiry_dates | {da:month for da in adjusted_weekly_expiries[:-1]}
                
                # # Assign 'W' for weekly expiries and 'M' for the last expiry of the month
                # temp = ['W'] * len(adjusted_weekly_expiries)
                # temp[-1] = 'M'
                # expiry_type.extend(temp)
        
        # Create a DataFrame with all expiry dates and expiry types
        week_expiry_df = pd.DataFrame.from_dict(weekly_expiry_dates, orient='index', columns=['ExpiryMonth']).reset_index().rename({"index":"Date"}, axis=1)
        month_expiry_df = pd.DataFrame.from_dict(monthly_expiry_dates, orient='index', columns=['ExpiryMonth']).reset_index().rename({"index":"Date"}, axis=1)

        week_expiry_df['Year'] = week_expiry_df['Date'].dt.year
        month_expiry_df['Year'] = month_expiry_df['Date'].dt.year

        week_expiry_df['WeekOfMonth'] = week_expiry_df.groupby(['Year','ExpiryMonth']).cumcount()+1
        
        # Assign <WeekNum>W for weekly expiries and 'M' for monthly expiry (last one in the month)
        week_expiry_df['ExpiryType'] = week_expiry_df['WeekOfMonth'].astype('int',errors = 'ignore').astype(str) + 'W'  
        month_expiry_df['ExpiryType'] = 'M'

        expiry_df = pd.concat([week_expiry_df, month_expiry_df])

        expiry_df['ExpiryMonth'] = pd.to_datetime(expiry_df['ExpiryMonth'],format='%m').dt.month_name()

        expiry_df["Month"] = expiry_df['Date'].dt.month_name()
        expiry_df['DayName'] = expiry_df['Date'].dt.day_name()
        expiry_df = expiry_df.sort_values(by='Date')

        expiry_df.drop(['WeekOfMonth','Year'],  axis=1, inplace=True)
        
        return expiry_df  
    
    def get_monthly_expiry_dates(self):
        """Generate monthly expiry dates for Calls, handling holidays."""
        years = self.year
        if isinstance(self.year, int):
            years = [self.year]
        elif not isinstance(self.year, list):
            raise ValueError("Years must be an integer or a list of integers.")
        monthly_expiry_dates = {}
        for year in years:
            for month in range(1, 13):
            # Get all the expiry days for the given weekday in the month
                all_expiry_days = self.get_all_weekdays_in_month(month, year)
                
                # Adjust each weekly expiry date for holidays

                adjusted_weekly_expiries = [self.get_trading_day_before(day) for day in all_expiry_days]
                monthly_expiry_dates[adjusted_weekly_expiries[-1]] = month
                # weekly_expiry_dates = weekly_expiry_dates | {da:month for da in adjusted_weekly_expiries[:-1]}
                
                # # Assign 'W' for weekly expiries and 'M' for the last expiry of the month
                # temp = ['W'] * len(adjusted_weekly_expiries)
                # temp[-1] = 'M'
                # expiry_type.extend(temp)
        
        # Create a DataFrame with all expiry dates and expiry types
        # week_expiry_df = pd.DataFrame.from_dict(weekly_expiry_dates, orient='index', columns=['ExpiryMonth']).reset_index().rename({"index":"Date"}, axis=1)
        month_expiry_df = pd.DataFrame.from_dict(monthly_expiry_dates, orient='index', columns=['ExpiryMonth']).reset_index().rename({"index":"Date"}, axis=1)

        # week_expiry_df['Year'] = week_expiry_df['Date'].dt.year
        month_expiry_df['Year'] = month_expiry_df['Date'].dt.year

        # week_expiry_df['WeekOfMonth'] = week_expiry_df.groupby('ExpiryMonth').cumcount()+1
        
        # Assign <WeekNum>W for weekly expiries and 'M' for monthly expiry (last one in the month)
        # week_expiry_df['ExpiryType'] = week_expiry_df['WeekOfMonth'].astype('int',errors = 'ignore').astype(str) + 'W'  
        month_expiry_df['ExpiryType'] = 'M'

        # expiry_df = pd.concat([week_expiry_df, month_expiry_df])

        month_expiry_df['ExpiryMonth'] = pd.to_datetime(month_expiry_df['ExpiryMonth'],format='%m').dt.month_name()

        month_expiry_df["Month"] = month_expiry_df['Date'].dt.month_name()
        month_expiry_df['DayName'] = month_expiry_df['Date'].dt.day_name()
        month_expiry_df = month_expiry_df.sort_values(by='Date')

        month_expiry_df.drop(['Year'],  axis=1, inplace=True)
        
        return month_expiry_df
