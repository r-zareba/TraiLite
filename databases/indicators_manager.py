import abc
import pandas as pd


class IndicatorManager(abc.ABC):
    @abc.abstractmethod
    def log(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_n_last_indicators(self, n: int, asset: str) -> pd.DataFrame:
        pass


class StochasticIndicatorManager(IndicatorManager):
    @abc.abstractmethod
    def log(self, asset: str, enter_k: float, enter_d: float, exit_k: float, exit_d: float):
        pass

    @abc.abstractmethod
    def get_n_last_indicators(self, n: int, asset: str) -> pd.DataFrame:
        pass


