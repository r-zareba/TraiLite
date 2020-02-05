import pandas as pd
import numpy as np


def apply_trading_fees(df: pd.DataFrame, fee: float) -> None:
    """
    Adds trading fees after position change - transaction been made
    """
    # df.loc[(df['Position'] != df['Position'].shift(1)), 'Strategy'] -= fee
    pass


class TradingRatiosCalculator:
    """
    Implementation of Trading Ratios calculator - ratios are calculated
    in lazy style only if specific method is called
    """
    __slots__ = ('_data', '_fee', '_drawdown_start', '_drawdown_end',
                 '_drawdown_period_calculated')

    def __init__(self, data: pd.DataFrame, fee: float) -> None:
        """
        :param data : pandas DataFrame with 'Position' columns
        :param fee: trading fee to apply after transaction made
        """
        self._data = data
        self._fee = fee

        self._drawdown_start = None
        self._drawdown_end = None
        self._drawdown_period_calculated = False

    def _calculate_market_equity(self):

        # self._data['Market Return'] = np.log(self._data['Close']).diff()
        self._data['Market'] = self._data['Close'].pct_change()

    def _calculate_strategy_equity(self):
        """
        Calculates trading strategy equity and apply trading fees
        """
        self._data['Strategy'] = (self._data['Market'] *
                                  self._data['Position'].shift(1))
        apply_trading_fees(self._data, self._fee)

    def _calculate_market_cumulative_return(self):
        """
        Calculates market cumulative return - take 1.0 at beginning
        and adds percentage changes over time
        """
        self._data['Market_return'] = self._data['Market'].cumsum() + 1

    def _calculate_strategy_cumulative_return(self):
        """
        Calculates strategy cumulative return - take 1.0 at beginning
        and adds percentage changes over time
        """
        self._data['Strategy_return'] = self._data['Strategy'].cumsum() + 1

    def fit(self):
        """
        Make necessary calculations to make
        calculating trading ratios possible
        """
        self._calculate_market_equity()
        self._calculate_strategy_equity()
        self._calculate_market_cumulative_return()
        self._calculate_strategy_cumulative_return()

    def _calculate_drawdown_period(self):
        df = self._data['Strategy_return'].dropna()
        self._drawdown_end = (np.maximum.accumulate(df) - df).idxmax()
        self._drawdown_start = (df[:self._drawdown_end]).idxmax()

        self._drawdown_period_calculated = True

    def calculate_market_return(self) -> float:
        """
        :return: last day cumulative return - total return of market
        (percentage change)
        """
        return self._data.iloc[
                   -1, self._data.columns.get_loc('Market_return')] - 1

    def calculate_strategy_return(self) -> float:
        """
        :return: last day cumulative return - total return of applied strategy
        (percentage change)
        """
        return self._data.iloc[
                -1, self._data.columns.get_loc('Strategy_return')] - 1

    def calculate_maximum_drawdown(self) -> float:
        if not self._drawdown_period_calculated:
            self._calculate_drawdown_period()

        df = self._data['Strategy_return'].dropna()
        return df[self._drawdown_start] - df[self._drawdown_end]

    def calculate_maximum_drawdown_period(self) -> pd.Timestamp:
        if not self._drawdown_period_calculated:
            self._calculate_drawdown_period()

        return self._drawdown_end - self._drawdown_start

    def calculate_num_of_transactions(self) -> int:
        """
        Calculates number of made transaction during backtest
        It counts only Long and Short enters, not exits
        """
        return self._data.loc[
                (self._data['Position'] != self._data['Position'].shift(1)) &
                (self._data['Position'].shift(1) == 0), 'Strategy'].count()
