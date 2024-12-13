import pandas as pd

class BaseIndicator:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with market data.
        
        Args:
            data (pd.DataFrame): Must contain columns like 'Close', 'volume', etc.
        """
        self.data = data
    
    def validate_columns(self, required_columns: list|str):
        """
        Validate that required columns exist in the data.
        """
        if type(required_columns)==list:
            missing = [col for col in required_columns if col not in self.data.columns]
        else:
            missing = [col for col in [required_columns] if col not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    

    def calculate_dma(self, data_series: pd.Series,period: int):
        """
        Calculate the Simple Moving Average (DMA).

        Args:
            data_series (pd.Series): data_series.
            period (int): Look-back period for the moving average.
        """
        return data_series.rolling(window=period).mean()

    def calculate_ema(self, data_series: pd.Series,period: int):
        """
        Calculate the Exponential Moving Average (EMA).

        Args:
            data_series (pd.Series): data_series.
            period (int): Look-back period for the EMA.
        """
        return data_series.ewm(span=period, adjust=False).mean()