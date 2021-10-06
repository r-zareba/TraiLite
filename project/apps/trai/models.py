import datetime as dt
from typing import List

from django.db import models


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class OHLC(models.Model):
    # Database fields (columns)
    asset = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    @classmethod
    def from_prices_list(cls, prices_list: List[float], asset: str):
        shifted_time = dt.datetime.now() - dt.timedelta(minutes=1)
        return cls(asset=asset,
                   timestamp=shifted_time,
                   open=prices_list[0],
                   high=max(prices_list),
                   low=min(prices_list),
                   close=prices_list[-1])

    def __str__(self):
        """ For nice, colorful printing """
        return f'{Color.BOLD}Timestamp - {Color.END} {self.timestamp}, ' \
               f'{Color.BOLD}Open - {Color.END} {self.open}, ' \
               f'{Color.BOLD}High - {Color.END} {self.high}, ' \
               f'{Color.BOLD}Low - {Color.END} {self.low}, ' \
               f'{Color.BOLD}Close - {Color.END} {self.close}'
