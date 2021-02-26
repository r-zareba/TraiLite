import abc
import pandas as pd

from databases.mongo.mongo_manager import MongoPricesManager
from trading_indicators import technical_indicators
from data_preprocessing import market_data_preprocessing
from settings import MONGO_HOST


n_minutes_dict = {
    '1T': 1,
    '5T': 5,
    '15T': 15,
    '30T': 30,
    '1H': 60
}


class IndicatorReader(abc.ABC):
    """
    Technical Indicator live monitor abstract class
    """
    __slots__ = ('_asset', '_enter_interval', '_exit_interval',
                 '_num_of_enter_m1', '_num_of_exit_m1', '_necessary_num_of_m1',
                 '_price_reader', '_n_ohlc_to_download', '_enter_df',
                 '_exit_df', '_are_indicators_calculated')

    def __init__(self, asset: str, enter_interval: str,
                 exit_interval: str) -> None:
        self._asset = asset
        self._enter_interval = enter_interval
        self._exit_interval = exit_interval

        self._num_of_enter_m1: int = n_minutes_dict[self._enter_interval]
        self._num_of_exit_m1: int = n_minutes_dict[self._exit_interval]
        self._necessary_num_of_m1: int = max(self._num_of_enter_m1,
                                             self._num_of_exit_m1)

        self._price_reader = MongoPricesManager(MONGO_HOST, self._asset)
        self._n_ohlc_to_download: int = self._get_n_ohlc_to_download()

        self._enter_df = pd.DataFrame()
        self._exit_df = pd.DataFrame()
        self._are_indicators_calculated: bool = False

    @property
    def hour(self) -> int:
        return self._enter_df['Hour'].iat[-1]

    @property
    def are_indicators_calculated(self) -> bool:
        return self._are_indicators_calculated

    @abc.abstractmethod
    def _get_n_ohlc_to_download(self) -> int:
        """
        Calculates minimum number of ohlc to download from MongoDB database
        necessary to calculate all needed indicators
        """
        pass

    @abc.abstractmethod
    def update_indicators(self):
        pass

    def _market_data_updated(self) -> bool:
        """
        Checks if ohlc received from price reader is long enough
        to calculate market dataframes
        :return: True of False
        """
        market_data = self._price_reader.get_n_last_ohlc(
            self._n_ohlc_to_download)

        if len(market_data) < self._n_ohlc_to_download:
            return False

        self._enter_df = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._enter_interval)
        self._exit_df = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._exit_interval)
        return True


class StochasticOscillatorReader(IndicatorReader):

    __slots__ = ('_enter_k_period', '_enter_smooth', '_enter_d_period',
                 '_exit_k_period', '_exit_smooth', '_exit_d_period')

    def __init__(self, asset: str, enter_interval: str, exit_interval: str,
                 enter_k_period: int, enter_smooth: int, enter_d_period: int,
                 exit_k_period: int, exit_smooth: int,
                 exit_d_period: int) -> None:

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
        return (necessary_periods * self._necessary_num_of_m1) + max_of_smooths + 20

    def update_indicators(self) -> None:
        if self._market_data_updated():
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

            if not self._are_indicators_calculated:
                self._are_indicators_calculated = True
        else:
            self._are_indicators_calculated = False

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
