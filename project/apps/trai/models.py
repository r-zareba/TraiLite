import datetime as dt
from typing import List

import pandas as pd
from django.db import models


def get_shifted_time() -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=1)


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
    asset = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=get_shifted_time)
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

    @classmethod
    def get_n_last_ohlc(cls, n: int, asset: str) -> pd.DataFrame:
        df = pd.DataFrame(cls.objects.filter(asset=asset).order_by('-timestamp')[:n].values())
        if df.empty:
            raise ValueError(f'\'{asset}\' does not have records in OHLC table')

        df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
        df.drop(['id', 'timestamp'], axis=1, inplace=True)
        return df.sort_index(ascending=True)

    def __str__(self):
        """ For nice, colorful printing """
        return f'{Color.BOLD}Timestamp - {Color.END} {self.timestamp}, ' \
               f'{Color.BOLD}Open - {Color.END} {self.open}, ' \
               f'{Color.BOLD}High - {Color.END} {self.high}, ' \
               f'{Color.BOLD}Low - {Color.END} {self.low}, ' \
               f'{Color.BOLD}Close - {Color.END} {self.close}'


class StochasticValues(models.Model):
    asset = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=get_shifted_time)
    enter_k = models.FloatField(null=True, blank=True)
    enter_d = models.FloatField(null=True, blank=True)
    exit_k = models.FloatField(null=True, blank=True)
    exit_d = models.FloatField(null=True, blank=True)

    @classmethod
    def get_n_last_stochastic(cls, n: int, asset: str) -> pd.DataFrame:
        df = pd.DataFrame(cls.objects.filter(asset=asset).order_by('-timestamp')[:n].values())
        if df.empty:
            raise ValueError(f'\'{asset}\' does not have records in OHLC table')

        df.set_index(pd.DatetimeIndex(df['timestamp']), inplace=True)
        df.drop(['id', 'timestamp'], axis=1, inplace=True)
        return df.sort_index(ascending=True)

    def __str__(self):
        return f'{self.asset}, {self.timestamp} - enter_k; {self.enter_k}, enter_d: {self.enter_d}, ' \
               f'exit_k: {self.exit_k}, exit_d: {self.exit_d}'


class Transaction(models.Model):
    asset = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=dt.datetime.now)
    action = models.IntegerField()
    comment = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.asset}, {self.timestamp} - action: {self.action}, comment: {self.comment}'
