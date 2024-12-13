import pandas as pd
from ..base_indicator import BaseIndicator

class MACDSignal(BaseIndicator):
    def __init__(self, close_prices, short_window=12, long_window=26, signal_window=9):
        """
        MACD signal class derived from BaseSignal.
        
        Parameters:
        - close_prices: A Pandas Series or list of closing prices.
        - short_window: Period for the short EMA (default: 12).
        - long_window: Period for the long EMA (default: 26).
        - signal_window: Period for the signal line EMA (default: 9).
        """
        super().__init__(close_prices)
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window

    def calculate(self):
        """
        Calculate the MACD line, signal line, and histogram.
        """
        macd_signal = pd.DataFrame()
        self.validate_columns(['Close'])
        short_ema = self.calculate_ema(self.data['Close'],self.short_window)
        long_ema = self.calculate_ema(self.data['Close'],self.long_window)
        macd_line = short_ema - long_ema
        signal_line = self.calculate_ema(macd_line, self.signal_window)
        histogram = macd_line - signal_line
        macd_signal['MACD_Line_Norm'] = macd_line/self.data['Close']
        macd_signal['MACD_Line'] = macd_line
        macd_signal['Signal_Line'] = signal_line
        macd_signal['Histogram'] = histogram
        # Add signals to the base class signals dictionary
        return macd_signal

    