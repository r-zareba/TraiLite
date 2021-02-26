import abc
import pandas as pd

from .ohlc import OHLC


class PricesManager(abc.ABC):
    """ Prices manager interface """
    @abc.abstractmethod
    def insert_ohlc(self, ohlc: OHLC) -> None:
        pass

    @abc.abstractmethod
    def get_n_last_ohlc(self, n: int) -> pd.DataFrame:
        pass

