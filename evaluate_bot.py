import argparse
import pandas as pd

from databases.mongo.mongo_manager import MongoPricesManager, MongoTransactionsManager
from settings import MONGO_HOST


# def main(asset: str, n_last: int):
asset = 'EURUSD'
n_last = 1000
prices_manager = MongoPricesManager(MONGO_HOST, asset)
transactions_logger = MongoTransactionsManager(MONGO_HOST, asset)

prices_df = prices_manager.get_n_last_ohlc(n_last)
tdf = transactions_logger.get_n_last_transactions(n_last)

longs = tdf.loc[tdf['Comment'] == 'Long', :]
closing_longs = tdf.loc[tdf['Comment'] == 'Closing Long', :]
shorts = tdf.loc[tdf['Comment'] == 'Short', :]
closing_shorts = tdf.loc[tdf['Comment'] == 'Closing Short', :]

transactions = pd.concat([tdf, prices_df], axis=1, join='inner').reset_index()
print('asd')


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--asset', type=str, help='Asset', required=True)
#     parser.add_argument('--n_last', type=int, help='n last OHLC prices to plot', default=1000)
#     args = parser.parse_args()
#     main(args.asset, args.n_last)
