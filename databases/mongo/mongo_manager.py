import abc
import datetime as dt

import pandas as pd
import pymongo

from databases.indicators_manager import StochasticIndicatorManager
from databases.ohlc import OHLC
from databases.prices_manager import PricesManager
from databases.transactions_manager import TransactionsManager
from databases.utils import SharedBetweenInstances
from databases.mongo.config import PRICES_DB_NAME, TRANSACTIONS_DB_NAME, STOCHASTIC_INDICATOR_DB_NAME


class MongoManager(abc.ABC):
    def __init__(self, host: str):
        self._mongo_client = pymongo.MongoClient(host)
        self._asset = None
        self._database = None
        self._collection = None

    def get_n_last_records(self, n: int) -> pd.DataFrame:
        """
        Gets n last records from object MongoDB collection
        Returns it as pandas Dataframe
        """
        df = pd.DataFrame(
            list(self._collection.find().limit(n).sort('$natural', -1)))
        if df.empty:
            raise ValueError(f'\'{self._asset}\' does not have records in '
                             f'\'{self._database.name}\' database!')

        df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
        df.drop('Timestamp', axis=1, inplace=True)
        return df.sort_index(ascending=True)


class MongoPricesManager(MongoManager, PricesManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, host: str, asset: str):
        super().__init__(host)
        self._asset = asset
        self._database = self._mongo_client[PRICES_DB_NAME]
        self._collection = self._database[self._asset]

    def insert_ohlc(self, ohlc: OHLC) -> None:
        ohlc_to_insert = {
            'Timestamp': ohlc.timestamp,
            'Open': ohlc.open,
            'High': ohlc.high,
            'Low': ohlc.low,
            'Close': ohlc.close}
        self._collection.insert_one(ohlc_to_insert)

    def get_n_last_ohlc(self, n: int) -> pd.DataFrame:
        return self.get_n_last_records(n)


class MongoTransactionsManager(MongoManager, TransactionsManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, host: str, asset: str):
        super().__init__(host)
        self._asset = asset
        self._database = self._mongo_client[TRANSACTIONS_DB_NAME]
        self._collection = self._database[asset]

    def log(self, action: int, comment: str) -> None:
        """ Inserts trading transaction to MongoDB transactions database """
        self._collection.insert_one({
            'Timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Action': action,
            'Comment': comment})

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


class MongoStochasticIndicatorManager(MongoManager, StochasticIndicatorManager):
    _mongo_client = SharedBetweenInstances()
    _database = SharedBetweenInstances()

    def __init__(self, host: str, asset: str):
        super().__init__(host)
        self._asset = asset
        self._database = self._mongo_client[STOCHASTIC_INDICATOR_DB_NAME]
        self._collection = self._database[asset]

    def log(self, enter_k: int, enter_d: int, exit_k: int, exit_d: int):
        self._collection.insert_one({
            'Timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Enter_K': round(enter_k, 2),
            'Enter_D': round(enter_d, 2),
            'Exit_K': round(exit_k, 2),
            'Exit_D': round(exit_d, 2)})

    def get_n_last_indicators(self, n: int) -> pd.DataFrame:
        return self.get_n_last_records(n)



