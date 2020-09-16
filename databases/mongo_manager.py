import pandas as pd


class MongoManager:
    def __init__(self):
        self._asset = None
        self._database = None
        self._collection = None

    def get_n_last_records(self, n: int) -> pd.DataFrame:
        df = pd.DataFrame(
            list(self._collection.find().limit(n).sort('$natural', -1)))
        if df.empty:
            raise ValueError(f'\'{self._asset}\' does not have records in '
                             f'\'{self._database.name}\' database!')

        df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
        df.drop('Timestamp', axis=1, inplace=True)
        return df.sort_index(ascending=True)
