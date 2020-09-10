import abc
import pandas as pd
import pymongo

import settings
from ohlc import OHLC


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


class PricesManager(abc.ABC):
    """ Prices manager interface """
    @abc.abstractmethod
    def insert_ohlc(self, ohlc: OHLC) -> None:
        pass

    @abc.abstractmethod
    def get_n_last_ohlc(self, n: int) -> pd.DataFrame:
        pass


class MongoPricesManager(PricesManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str, host=''):
        self._asset = asset
        if host:
            self._mongo_client = pymongo.MongoClient(host)
        else:
            self._mongo_client = pymongo.MongoClient(settings.MONGO_HOST)

        self._database = self._mongo_client[settings.PRICES_COLLECTION_NAME]
        self._collection = self._database[self._asset]

    def insert_ohlc(self, ohlc: OHLC) -> None:
        ohlc_to_insert = {
            'Timestamp': ohlc.timestamp,
            'Open': ohlc.open,
            'High': ohlc.high,
            'Low': ohlc.low,
            'Close': ohlc.close}
        self._collection.insert_one(ohlc_to_insert)
        print(f'OHLC inserted: {ohlc}')

    def get_n_last_ohlc(self, n: int) -> pd.DataFrame:
        """
        Gets n last records from object MongoDB collection
        Returns it as pandas Dataframe
        """
        df = pd.DataFrame(
            list(self._collection.find().limit(n).sort('$natural', -1)))
        df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
        df.drop('Timestamp', axis=1, inplace=True)
        # df.loc[:, 'Timestamp'] = df['Timestamp'].apply(lambda x: x.round('T'))
        return df.sort_index(ascending=True)
