# bollinger.py
import pandas as pd
from ..base_indicator import BaseIndicator

class BollingerBands(BaseIndicator):
    def __init__(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0):
        super().__init__(data)
        self.period = period
        self.std_dev = std_dev
    
    def calculate(self):
        bollinger_signal = pd.DataFrame()
        self.validate_columns(['Close'])

        bollinger_signal['rolling_mean'] = self.calculate_dma(self.data['Close'],self.period)
        bollinger_signal['rolling_std'] = self.data['Close'].rolling(window=self.period).std()
        bollinger_signal['upper_band'] = bollinger_signal['rolling_mean'] + (self.std_dev * bollinger_signal['rolling_std'])
        bollinger_signal['lower_band'] = bollinger_signal['rolling_mean'] - (self.std_dev * bollinger_signal['rolling_std'])
        return bollinger_signal