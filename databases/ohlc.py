import datetime as dt


class OHLC:
    __slots__ = ('timestamp', 'open', 'high', 'low', 'close')

    def __init__(self, timestamp: str, open: float, high: float,
                 low: float, close: float):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    @classmethod
    def from_prices_list(cls, prices_list: list):
        shifted_time = dt.datetime.now() - dt.timedelta(minutes=1)
        return cls(timestamp=shifted_time.strftime('%Y-%m-%d %H:%M:%S'),
                   open=prices_list[0],
                   high=max(prices_list),
                   low=min(prices_list),
                   close=prices_list[-1])

    def __str__(self):
        return f'Timestamp - {self.timestamp}, Open - {self.open},' \
               f' High - {self.high}, Low - {self.low}, Close - {self.close}'
