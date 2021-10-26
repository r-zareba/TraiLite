import pandas as pd


def add_hour_column(df: pd.DataFrame) -> None:
    if isinstance(df.index, pd.DatetimeIndex):
        df.loc[:, 'Hour'] = df.index.hour
    else:
        raise TypeError('Cannot add Hour to non-datetime index dataframe!')


def get_resampled_ohlc_df(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    if isinstance(df.index, pd.DatetimeIndex):
        return df.resample(interval).agg({'open': 'first',
                                          'high': 'max',
                                          'low': 'min',
                                          'close': 'last'})

    else:
        raise TypeError('Cannot resample non-datetime index dataframe!')


def prepare_market_df(market_data: pd.DataFrame, interval: str) -> pd.DataFrame:
    if interval == '1T':
        add_hour_column(market_data)
        return market_data

    resampled_df = get_resampled_ohlc_df(df=market_data, interval=interval)
    add_hour_column(resampled_df)
    return resampled_df
