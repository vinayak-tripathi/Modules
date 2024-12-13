import pandas as pd
from ..base_indicator import BaseIndicator

class RSISignal(BaseIndicator):
    def __init__(self, close_prices, period=14):
        """
        RSI signal class derived from BaseSignal.
        
        Parameters:
        - close_prices: A Pandas Series or list of closing prices.
        - period: The look-back period for RSI calculation (default: 14).
        """
        super().__init__(close_prices)
        self.period = period

    def calculate(self):
        """
        Calculate the Relative Strength Index (RSI).
        """
        rsi_signal = pd.DataFrame()
        delta = self.data['Close'].pct_change()
        # gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        # loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        # rs = gain / loss

        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        gain_roll_avg = self.calculate_ema((delta.where(delta > 0, 0)), self.period)
        loss_roll_avg = self.calculate_ema((-delta.where(delta < 0, 0)), self.period)

        rs = gain_roll_avg / loss_roll_avg
        rsi = 100 - (100 / (1 + rs))
        rsi_signal['RSI'] = rsi
        
        # Add RSI to the signals dictionary
        return rsi_signal
