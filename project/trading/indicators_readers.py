import abc
import pandas as pd

from trading import technical_indicators
from data_preprocessing import market_data_preprocessing

from trai.models import OHLC, StochasticValues


n_minutes_dict = {
    '1T': 1,
    '5T': 5,
    '15T': 15,
    '30T': 30,
    '1H': 60
}


class IndicatorReader:
    """ Technical Indicator live monitor abstract class """
    __slots__ = ('_asset', '_enter_interval', '_exit_interval', '_num_of_enter_m1', '_num_of_exit_m1',
                 '_max_interval', '_n_ohlc_to_download', '_enter_df', '_exit_df', '_are_indicators_calculated')

    def __init__(self, asset: str, enter_interval: str, exit_interval: str):
        self._asset = asset
        self._enter_interval = enter_interval
        self._exit_interval = exit_interval

        self._num_of_enter_m1 = n_minutes_dict[self._enter_interval]
        self._num_of_exit_m1 = n_minutes_dict[self._exit_interval]
        self._max_interval = max(self._num_of_enter_m1, self._num_of_exit_m1)

        self._n_ohlc_to_download = self._get_n_ohlc_to_download()
        self._enter_df = pd.DataFrame()
        self._exit_df = pd.DataFrame()
        self._are_indicators_calculated = False

    @property
    def hour(self) -> int:
        return self._enter_df['Hour'].iat[-1]

    @property
    def are_indicators_calculated(self) -> bool:
        return self._are_indicators_calculated

    @abc.abstractmethod
    def _get_n_ohlc_to_download(self) -> int:
        """ Calculates minimum number of ohlc to download from database necessary to calculate all indicators """
        pass

    @abc.abstractmethod
    def update_indicators(self):
        pass

    def _market_data_updated(self) -> bool:
        """
        Checks if ohlc received from price reader is long enough
        to calculate necessary market dataframes
        """
        market_data = OHLC.get_n_last_ohlc(self._n_ohlc_to_download, self._asset)

        print(f'{self._asset}, n to download: {self._n_ohlc_to_download}')

        if len(market_data) < self._n_ohlc_to_download:
            return False

        self._enter_df = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._enter_interval)
        self._exit_df = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._exit_interval)

        # print(f'{self._asset}, N to download: {self._n_ohlc_to_download}')
        # print(f'{self._asset} ENTER SHAPE: {self._enter_df.shape}')
        # print(f'{self._asset} ENTER COLUMNS: {self._enter_df.columns}')
        # print(f'{self._asset} EXIT SHAPE: {self._exit_df.shape}')
        # print(f'{self._asset} EXIT COLUMNS: {self._exit_df.columns}')

        return True


class StochasticOscillatorReader(IndicatorReader):
    __slots__ = ('_enter_k_period', '_enter_smooth', '_enter_d_period',
                 '_exit_k_period', '_exit_smooth', '_exit_d_period')

    def __init__(self, asset: str, enter_interval: str, exit_interval: str, enter_k_period: int, enter_smooth: int,
                 enter_d_period: int, exit_k_period: int, exit_smooth: int, exit_d_period: int,):

        self._enter_k_period = enter_k_period
        self._enter_smooth = enter_smooth
        self._enter_d_period = enter_d_period
        self._exit_k_period = exit_k_period
        self._exit_smooth = exit_smooth
        self._exit_d_period = exit_d_period
        super().__init__(asset, enter_interval, exit_interval)

    # TODO properties for testing - remove later
    @property
    def enter_df(self):
        return self._enter_df

    @property
    def exit_df(self):
        return self._exit_df

    def _get_n_ohlc_to_download(self) -> int:
        necessary_periods = max(
            self._enter_k_period, self._enter_d_period,
            self._exit_k_period, self._exit_d_period)
        max_of_smooths = max(self._enter_smooth, self._exit_smooth)
        # TODO calculate optimum num of records from DB
        return (necessary_periods * self._max_interval) + max_of_smooths + 30

    def update_indicators(self) -> bool:
        if not self._market_data_updated():
            return False

        technical_indicators.StochasticOscillator.apply_full_stochastic_to_df(
            df=self._enter_df,
            k_period=self._enter_k_period,
            smooth=self._enter_smooth,
            d_period=self._enter_d_period)

        technical_indicators.StochasticOscillator.apply_full_stochastic_to_df(
            df=self._exit_df,
            k_period=self._exit_k_period,
            smooth=self._exit_smooth,
            d_period=self._exit_d_period)

        stochastic_values = StochasticValues(
            asset=self._asset,
            enter_k=self.current_enter_k,
            enter_d=self.current_enter_d,
            exit_k=self.current_exit_k,
            exit_d=self.current_exit_d)

        print(f'{self._asset}, enter shape: {self._enter_df.shape}')
        print(f'{self._asset}, exit shape: {self._exit_df.shape}')

        print(f'{self._asset}, enter tail {self._enter_df.tail()}')
        print(f'{self._asset}, exit tail {self._exit_df.tail()}')
        print(stochastic_values)

        stochastic_values.save()
        return True

    @property
    def current_enter_k(self) -> float:
        return self._enter_df['K'].iat[-1]

    @property
    def current_enter_d(self) -> float:
        return self._enter_df['D'].iat[-1]

    @property
    def previous_enter_k(self) -> float:
        return self._enter_df['K'].iat[-2]

    @property
    def previous_enter_d(self) -> float:
        return self._enter_df['D'].iat[-2]

    @property
    def current_exit_k(self) -> float:
        return self._exit_df['K'].iat[-1]

    @property
    def current_exit_d(self) -> float:
        return self._exit_df['D'].iat[-1]

    @property
    def previous_exit_k(self) -> float:
        return self._exit_df['K'].iat[-2]

    @property
    def previous_exit_d(self) -> float:
        return self._exit_df['D'].iat[-2]
