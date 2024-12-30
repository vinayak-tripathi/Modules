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

    def get_all_expiry_dates(self):
        """Generate weekly and monthly expiry dates for Calls, handling holidays."""
        weekly_expiry_dates = []
        years = self.year
        if isinstance(self.year, int):
            years = [self.year]
        elif not isinstance(self.year, list):
            raise ValueError("Years must be an integer or a list of integers.")
        print(years)
        for year in years:
            for month in range(1, 13):
                # Get all the expiry days for the given weekday in the month
                all_expiry_days = self.get_all_weekdays_in_month(month, year)
                
                # Adjust each weekly expiry date for holidays
                adjusted_weekly_expiries = [self.get_trading_day_before(day) for day in all_expiry_days]
                weekly_expiry_dates.extend(adjusted_weekly_expiries)
                
                # # Assign 'W' for weekly expiries and 'M' for the last expiry of the month
                # temp = ['W'] * len(adjusted_weekly_expiries)
                # temp[-1] = 'M'
                # expiry_type.extend(temp)
        
        # Create a DataFrame with all expiry dates and expiry types
        expiry_df = pd.DataFrame({
            'ExpiryDay':self.expiry_day_name,
            'Date': weekly_expiry_dates,
            'ExpiryType': np.nan
        })
        expiry_df["Month"] = expiry_df['Date'].dt.month_name()
        expiry_df['DayName'] = expiry_df['Date'].dt.day_name()

        expiry_df['Year'] = expiry_df['Date'].dt.year
        expiry_df['WeekOfMonth'] = expiry_df['Date'].apply(lambda x: (x.day - 1) // 7 + 1)
        
        last_expiry_per_month = expiry_df.groupby(['Month','Year','ExpiryDay'])['Date'].apply(np.max).values

        # Assign <WeekNum>W for weekly expiries and 'M' for monthly expiry (last one in the month)
        expiry_df['ExpiryType'] = expiry_df['WeekOfMonth'].astype(str) + 'W'
        expiry_df.loc[expiry_df['Date'].isin(last_expiry_per_month), 'ExpiryType'] = 'M'
        expiry_df.drop(['WeekOfMonth','Year'],  axis=1, inplace=True)
        
        return expiry_df  
    
    def get_monthly_expiry_dates(self):
        """Generate monthly expiry dates for Calls, handling holidays."""
        weekly_expiry_dates = []
        years = self.year
        if isinstance(self.year, int):
            years = [self.year]
        elif not isinstance(self.year, list):
            raise ValueError("Years must be an integer or a list of integers.")
        print(years)
        for year in years:
            for month in range(1, 13):
                # Get all the expiry days for the given weekday in the month
                all_expiry_days = self.get_all_weekdays_in_month(month, year)
                
                # Adjust each weekly expiry date for holidays
                adjusted_weekly_expiries = [self.get_trading_day_before(day) for day in all_expiry_days]
                weekly_expiry_dates.extend(adjusted_weekly_expiries)
                
                # # Assign 'W' for weekly expiries and 'M' for the last expiry of the month
                # temp = ['W'] * len(adjusted_weekly_expiries)
                # temp[-1] = 'M'
                # expiry_type.extend(temp)
        
        # Create a DataFrame with all expiry dates and expiry types
        expiry_df = pd.DataFrame({
            'ExpiryDay':self.expiry_day_name,
            'Date': weekly_expiry_dates,
            'ExpiryType': np.nan
        })
        expiry_df["Month"] = expiry_df['Date'].dt.month_name()
        expiry_df['DayName'] = expiry_df['Date'].dt.day_name()

        expiry_df['WeekOfMonth'] = expiry_df['Date'].apply(lambda x: (x.day - 1) // 7 + 1)
        
        last_expiry_per_month = expiry_df.groupby('Month')['WeekOfMonth'].transform("max")

        # Assign <WeekNum>W for weekly expiries and 'M' for monthly expiry (last one in the month)
        expiry_df['ExpiryType'] = expiry_df['WeekOfMonth'].astype(str) + 'W'
        expiry_df.loc[expiry_df['WeekOfMonth'] == last_expiry_per_month, 'ExpiryType'] = 'M'
        expiry_df.drop(['WeekOfMonth'],  axis=1, inplace=True)
        

        return expiry_df
