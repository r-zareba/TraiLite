import abc
import datetime as dt
import pandas as pd
import pymongo

import settings
from .mongo_manager import MongoManager


class SharedBetweenInstances:
    """
    Implementation of Shared Attribute Descriptor
    Safe way of keeping same Database client for all instances
    """
    def __init__(self, initial_value=None):
        self.value = initial_value
        self._name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.value is None:
            raise AttributeError(f'{self._name} was never set')
        return self.value

    def __set__(self, instance, new_value):
        self.value = new_value

    def __set_name__(self, owner, name):
        self._name = name


class TransactionsManager(abc.ABC):
    """ Database transaction logger interface """
    @abc.abstractmethod
    def log(self, action: int, comment: str) -> None:
        pass

    @abc.abstractmethod
    def get_n_last_transactions(self, n: int) -> pd.DataFrame:
        pass


class MongoTransactionsManager(MongoManager, TransactionsManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str, host=''):
        super().__init__()
        if host:
            self._mongo_client = pymongo.MongoClient(host)
        else:
            self._mongo_client = pymongo.MongoClient(settings.MONGO_HOST)
        self._asset = asset
        self._database = self._mongo_client['transactions']
        self._collection = self._database[asset]

    def log(self, action: int, comment: str) -> None:
        """ Inserts trading transaction to MongoDB transactions database """
        transaction = {
            'Timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Action': action,
            'Comment': comment
        }
        self._collection.insert_one(transaction)

    def get_n_last_transactions(self, n: int) -> pd.DataFrame:
        return self.get_n_last_records(n)

    def get_current_position(self) -> int:
        try:
            last_transaction = self.get_n_last_transactions(1)
        except Exception as e:
            return 0
        else:
            if 'closing' in last_transaction['Comment'].str.lower().values[0]:
                return 0
            elif 'long' in last_transaction['Comment'].str.lower().values[0]:
                return 1
            elif 'short' in last_transaction['Comment'].str.lower().values[0]:
                return -1
