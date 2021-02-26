import abc
import pandas as pd


class TransactionsManager(abc.ABC):
    """ Database transaction logger interface """
    @abc.abstractmethod
    def log(self, action: int, comment: str) -> None:
        pass

    @abc.abstractmethod
    def get_n_last_transactions(self, n: int) -> pd.DataFrame:
        pass
