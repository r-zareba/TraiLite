import pandas as pd


class StochasticOscillator:
    """
    https://analizy.investio.pl/oscylator-stochastyczny-stochastic-oscillator/
    """
    __slots__ = ()

    @staticmethod
    def apply_full_stochastic_to_df(df: pd.DataFrame, k_period: int, smooth: int, d_period: int) -> None:
        """
        Calculates full stochastic indicator
        Adds K and D columns to received dataframe
        """
        low = df['low'].rolling(window=k_period).min()
        high = df['high'].rolling(window=k_period).max()

        k_value = ((df['close'] - low) / (high - low)) * 100
        df.loc[:, 'K'] = k_value.rolling(window=smooth).mean()
        df.loc[:, 'D'] = df['K'].rolling(window=d_period).mean()


class SimpleMovingAverage:
    __slots__ = ()

    @staticmethod
    def sma(df_column: pd.Series, period: int) -> pd.Series:
        """
        Simple moving average
        :param df_column: pandas DataFrame column
        :param period: number of periods
        :return: dataframe column
        """
        return df_column.rolling(window=period).mean()


class ExponentialMovingAverage:
    __slots__ = ()

    @staticmethod
    def ema(df_column: pd.Series, period: int) -> pd.Series:
        """
        Exponential moving average
        :param df_column: pandas DataFrame column
        :param period: number of periods
        :return: dataframe column
        """
        return df_column.ewm(span=period).mean()

    # TODO to finish
