import pandas as pd
from .indicators import BollingerBands
from .indicators import MACDSignal
from .indicators import RSISignal

class MainIndicator:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with market data.
        
        Args:
            data (pd.DataFrame): Market data with columns like 'close', 'volume', etc.
        """
        self.data = data
        self.indicators = {}

    def calculate_bollinger_bands(self, period=20, std_dev=2.0):
        """
        Calculate Bollinger Bands and attach results to the data.
        """
        print("bOLL")
        bb = BollingerBands(self.data, period, std_dev)
        bollinger_signal = bb.calculate()
        self.indicators['bollinger'] = bollinger_signal
        return self.indicators['bollinger']
    
    def calculate_macd(self, short_period=12, long_period=26, signal_period=9):
        """
        Calculate MACD and attach results to the data.
        """
        macd = MACDSignal(self.data, short_period, long_period, signal_period)
        macd_signal = macd.calculate()
        self.indicators['macd'] = macd_signal
        return self.indicators['macd']

    def calculate_rsi(self, period=20):
        """
        Calculate RSI and attach results to the data.
        """
        rsi = RSISignal(self.data, period)
        rsi_signal = rsi.calculate()
        self.indicators['rsi'] = rsi_signal
        return self.indicators['rsi']

    def get_indicator(self, name):
        """
        Retrieve specific indicator results by name.
        """
        return self.indicators.get(name, None)