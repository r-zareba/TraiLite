import abc
import pandas as pd

from .ohlc import OHLC


class PricesManager(abc.ABC):
    """ Prices manager interface """
    @abc.abstractmethod
    def insert_ohlc(self, ohlc: OHLC, asset: str):
        pass

    @abc.abstractmethod
    def get_n_last_ohlc(self, n: int, asset: str) -> pd.DataFrame:
        pass

