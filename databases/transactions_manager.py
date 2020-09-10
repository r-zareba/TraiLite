import abc
import datetime as dt
import pandas as pd
import pymongo

import settings


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


class MongoTransactionsManager(TransactionsManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str, host=''):
        if host:
            self._mongo_client = pymongo.MongoClient(host)
        else:
            self._mongo_client = pymongo.MongoClient(settings.MONGO_HOST)
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
        df = pd.DataFrame(
            list(self._collection.find().limit(n).sort('$natural', -1)))
        df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
        df.drop('Timestamp', axis=1, inplace=True)
        return df.sort_index(ascending=True)
