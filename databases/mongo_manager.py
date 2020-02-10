import datetime as dt
import pandas as pd
import pymongo


class SharedBetweenInstances:
    """
    Implementation of Shared Attribute Descriptor
    Safe way of keeping same Mongo DB client for all instances
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


class BaseMongoPrices:
    """ Base Class of Mongo DB Prices database manipulation """
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str) -> None:
        self._asset = asset
        self._mongo_client = pymongo.MongoClient()
        self._database = self._mongo_client['prices']
        self._collection = self._database[self._asset]


class MongoPricesWriter(BaseMongoPrices):
    """ Implementation of Mongo DB market prices writer interface """
    def __init__(self, asset: str) -> None:
        super().__init__(asset)

    def insert_ohlc(self, shared_list: list) -> None:
        """
        Inserts OHLC to prices/asset MongoDB collection
        :param shared_list: list of prices shared between processes (workers)
        """
        shifted_time = dt.datetime.now() - dt.timedelta(minutes=1)

        ohlc = {'Timestamp': shifted_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Open': shared_list[0],
                'High': max(shared_list),
                'Low': min(shared_list),
                'Close': shared_list[-1]}
        self._collection.insert_one(ohlc)


class MongoPricesReader(BaseMongoPrices):
    """ Implementation of Mongo DB Prices interface """
    def __init__(self, asset: str) -> None:
        super().__init__(asset)

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


class MongoTransactionsLogger:
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, username: str):
        self._username = username
        self._mongo_client = pymongo.MongoClient()
        self._database = self._mongo_client['transactions']
        self._collection = self._database[self._username]

    def log_transaction(self, asset: str, position: int, comment: str) -> None:
        """ Inserts trading transaction to MongoDB transactions database """
        transaction = {
            'Timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Asset': asset,
            'Position': position,
            'Comment': comment
        }
        self._collection.insert_one(transaction)
