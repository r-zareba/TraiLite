import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from databases.mongo.mongo_manager import MongoPricesManager, MongoTransactionsManager, MongoStochasticIndicatorManager
from settings import MONGO_HOST


def main(asset: str, n_last: int):
    prices_manager = MongoPricesManager(MONGO_HOST, asset)
    transactions_logger = MongoTransactionsManager(MONGO_HOST, asset)
    indicator_manager = MongoStochasticIndicatorManager(MONGO_HOST, asset)

    prices_df = prices_manager.get_n_last_ohlc(n_last)
    tdf = transactions_logger.get_n_last_transactions(n_last)
    indicators = indicator_manager.get_n_last_indicators(n_last)

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
    indicators.reset_index(inplace=True)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    fig.add_trace(
        go.Ohlc(x=prices_df['Timestamp'],
                open=prices_df['Open'],
                high=prices_df['High'],
                low=prices_df['Low'],
                close=prices_df['Close'],
                name=asset), row=1, col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)

    for transaction_df in (longs, closing_longs, shorts, closing_shorts):
        fig.add_trace(
            go.Scatter(x=transaction_df['Timestamp'],
                       y=transaction_df['Close'],
                       mode='markers',
                       name=str(transaction_df['Comment'].unique()),
                       marker=dict(size=10, line=dict(width=2, color='White'))), row=1, col=1)

    for stoch_type in ('Enter_K', 'Enter_D'):
        fig.add_trace(
            go.Scatter(x=indicators['Timestamp'],
                       y=indicators[stoch_type],
                       name=stoch_type), row=2, col=1)

    for stoch_type in ('Exit_K', 'Exit_D'):
        fig.add_trace(
            go.Scatter(x=indicators['Timestamp'],
                       y=indicators[stoch_type],
                       name=stoch_type), row=3, col=1)

    fig.update_layout(title_text=asset)
    fig.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=str, help='Asset', required=True)
    parser.add_argument('--n_last', type=int, help='n last OHLC prices to plot', default=1000)
    args = parser.parse_args()
    main(args.asset, args.n_last)
