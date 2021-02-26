import argparse
import pandas as pd
import plotly.graph_objects as go

import sys
sys.path.insert(0, './databases')

from databases.mongo.mongo_manager import MongoPricesManager, MongoTransactionsManager
from settings import MONGO_HOST


def main(args):
    asset = args.asset
    prices_manager = MongoPricesManager(MONGO_HOST, asset)
    transactions_logger = MongoTransactionsManager(MONGO_HOST, asset)

    prices_df = prices_manager.get_n_last_ohlc(1000)
    tdf = transactions_logger.get_n_last_transactions(1000)

    longs = tdf.loc[tdf['Comment'] == 'Long', :]
    closing_longs = tdf.loc[tdf['Comment'] == 'Closing Long', :]
    shorts = tdf.loc[tdf['Comment'] == 'Short', :]
    closing_shorts = tdf.loc[tdf['Comment'] == 'Closing Short', :]

    longs = pd.concat([longs, prices_df], axis=1, join='inner').reset_index()
    closing_longs = pd.concat(
        [closing_longs, prices_df], axis=1, join='inner').reset_index()
    shorts = pd.concat([shorts, prices_df], axis=1, join='inner').reset_index()
    closing_shorts = pd.concat(
        [closing_shorts, prices_df], axis=1, join='inner').reset_index()

    prices_df.reset_index(inplace=True)

    fig = go.Figure(data=go.Ohlc(
        x=prices_df['Timestamp'],
        open=prices_df['Open'],
        high=prices_df['High'],
        low=prices_df['Low'],
        close=prices_df['Close'],
        name=asset))

    fig.update(layout_xaxis_rangeslider_visible=False)

    for transaction_df in (longs, closing_longs, shorts, closing_shorts):
        fig.add_trace(go.Scatter(x=transaction_df['Timestamp'],
                                 y=transaction_df['Close'],
                                 mode='markers',
                                 name=str(transaction_df['Comment'].unique()),
                                 marker=dict(
                                     size=10,
                                     line=dict(width=2, color='White'))))
    fig.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=str, help='Asset', required=True)
    passed_args = parser.parse_args()
    main(passed_args)
