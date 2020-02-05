import pandas as pd


def add_hour_column(df: pd.DataFrame) -> None:
    """
    Adds Hour column to pandas dataframe with datetime index
    :param df: pandas DataFrame with DateTime index
    """
    if isinstance(df.index, pd.DatetimeIndex):
        df.loc[:, 'Hour'] = df.index.hour
    else:
        raise TypeError('Cannot add Hour to non-datetime index dataframe!')


def resample_dataframe(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """
    :param df: pandas DataFrame with DateTime index
    :param interval: for example '1T', '5T', '1H'
    :return: Spacefic time period resampled dataframe
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return df.resample(interval).bfill()
    else:
        raise TypeError('Cannot resample non-datetime index dataframe!')


def prepare_market_df(market_data: pd.DataFrame,
                      interval: str) -> pd.DataFrame:
    """
    Prepares market dataframe for indicators calculations
    :param market_data: pandas DataFrame with datetime index
    :param interval: for example '1T', '5T', '1H'
    :return: prepared pandas DataFrame
    """
    add_hour_column(market_data)
    if interval != '1T':
        return resample_dataframe(df=market_data, interval=interval)
    else:
        return market_data
