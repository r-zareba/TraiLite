import abc
import pandas as pd


class TransactionsManager(abc.ABC):
    """ Database transaction logger interface """
    @abc.abstractmethod
    def log(self, action: int, comment: str, asset: str) -> None:
        pass

    @abc.abstractmethod
    def get_n_last_transactions(self, n: int, asset: str) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_current_position(self, asset: str) -> int:
        pass
