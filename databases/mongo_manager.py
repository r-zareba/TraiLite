import datetime as dt

import pandas as pd
import pymongo

import settings
from database_manager import DatabaseManager, SharedBetweenInstances
from ohlc import OHLC


class MongoManager(DatabaseManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str):
        self._asset = asset
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


class MongoTransactionsLogger:
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, asset: str):
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
