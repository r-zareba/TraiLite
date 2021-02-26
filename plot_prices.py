import argparse
import plotly.graph_objects as go

import sys
sys.path.insert(0, './databases')

from databases.mongo.mongo_manager import MongoPricesManager

MONGO_HOST = 'mongodb://localhost:27017/'


def main(args):
    asset = args.asset
    prices_manager = MongoPricesManager(asset, host=MONGO_HOST)
    prices_df = prices_manager.get_n_last_ohlc(1000).reset_index()

    fig = go.Figure(data=go.Ohlc(
        x=prices_df['Timestamp'],
        open=prices_df['Open'],
        high=prices_df['High'],
        low=prices_df['Low'],
        close=prices_df['Close'],
        name=asset))

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', type=str, help='Asset', required=True)
    passed_args = parser.parse_args()
    main(passed_args)
