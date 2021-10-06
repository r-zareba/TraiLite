import abc
import numpy as np
import pandas as pd

import file_readers
import trading_ratios

import sys
sys.path.insert(0, '../data_preprocessing')
sys.path.insert(0, '../trading_indicators')
import market_data_preprocessing
import technical_indicators


class BaseTechnicalsBacktester:
    """ Base class for technical strategies backtesting """
    __slots__ = ('_enter_interval', '_exit_interval', '_start_hour',
                 '_end_hour', '_fee', '_data', '_exit_df',
                 '_long_enter_condition', '_long_exit_condition',
                 '_short_enter_condition', '_short_exit_condition',
                 '_is_strategy_applied', '_ratios_calculator')

    def __init__(self, enter_interval: str, exit_interval: str, start_hour: int,
                 end_hour: int, fee: float):
        """
        :param enter_interval:
         interval for calculating position enter '%D', '%H', '%T'
        :param exit_interval:
         interval for calculating position exit '%D', '%H', '%T'
        :param start_hour: trading start hour
        :param end_hour: trading end hour
        :param fee: trading fee (spread)
        """
        self._enter_interval = enter_interval
        self._exit_interval = exit_interval
        self._start_hour = start_hour
        self._end_hour = end_hour
        self._fee = fee

        self._data = pd.DataFrame()
        self._exit_df = pd.DataFrame()

        self._long_enter_condition = pd.Series()
        self._long_exit_condition = pd.Series()
        self._short_enter_condition = pd.Series()
        self._short_exit_condition = pd.Series()

        self._is_strategy_applied: bool = False
        self._ratios_calculator: trading_ratios.TradingRatiosCalculator = None

    @abc.abstractmethod
    def _calculate_indicators(self):
        pass

    @abc.abstractmethod
    def _set_long_positions_logic(self):
        pass

    @abc.abstractmethod
    def _set_short_positions_logic(self):
        pass

    @property
    def data(self):
        """
        :return: pandas Dataframe for analytics / plotting purposes
        """
        if self._is_strategy_applied:
            return self._data.dropna()
        else:
            raise ValueError(
                'No purpose for returning dataframe, '
                'with no strategy applied!')

    def _apply_long_positions(self) -> None:
        """ Applies Long positions logic to dataframe """
        self._set_long_positions_logic()
        self._data['Long'] = np.nan
        self._data.loc[self._long_enter_condition, 'Long'] = 1
        self._data.loc[self._long_exit_condition, 'Long'] = 0

    def _apply_short_positions(self) -> None:
        """ Applies Short positions logic to dataframe """
        self._set_short_positions_logic()
        self._data['Short'] = np.nan
        self._data.loc[self._short_enter_condition, 'Short'] = -1
        self._data.loc[self._short_exit_condition, 'Short'] = 0

    def _apply_strategy_positions(self) -> None:
        self._calculate_indicators()
        self._apply_long_positions()
        self._apply_short_positions()

        for position in ['Long', 'Short']:
            self._data.iloc[0, self._data.columns.get_loc(position)] = 0
            self._data[position] = self._data[position].fillna(method='ffill')

        self._data['Position'] = self._data['Long'] + self._data['Short']
        self._is_strategy_applied = True

    def _fit(self):
        """ Applies all backtest process """
        self._apply_strategy_positions()
        self._ratios_calculator = trading_ratios.TradingRatiosCalculator(
            data=self._data, fee=self._fee)
        self._ratios_calculator.fit()

    def fit_from_data(self, market_data: pd.DataFrame) -> None:
        """
        Runs initialized backtester using received data
        :param market_data : prepared market data DataFrame contains price
        columns, datetime index, 'Hour' column
        """
        self._data = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._enter_interval)

        self._exit_df = market_data_preprocessing.prepare_market_df(
            market_data=market_data, interval=self._exit_interval)

        self._fit()

    def fit_from_file(self, file_path: str, file_source: str) -> None:
        """
        Creates csv loader object based on received csv source, loads data
        and fits the backtester
        :param file_path: full path to file like '/home/user/dir/EURUSD.csv'
        :param file_source: for example 'dukascopy'
        """
        file_reader = file_readers.FileReaderFactory(
            file_path, file_source).get_file_reader()

        market_data = file_reader.read_data()
        self.fit_from_data(market_data=market_data)

    @property
    def market_return(self):
        return self._ratios_calculator.calculate_market_return()

    @property
    def strategy_return(self):
        return self._ratios_calculator.calculate_strategy_return()

    @property
    def maximum_drawdown(self):
        return self._ratios_calculator.calculate_maximum_drawdown()

    @property
    def maximum_drawdown_period(self):
        return self._ratios_calculator.calculate_maximum_drawdown_period()

    @property
    def num_of_transactions(self):
        return self._ratios_calculator.calculate_num_of_transactions()


class StochasticOscilatorBacktester(BaseTechnicalsBacktester):
    """ Implementation of backtesting based on Stochastic Oscilator """
    __slots__ = ('_enter_k_period', '_enter_smooth', '_enter_d_period',
                 '_exit_k_period', '_exit_smooth', '_exit_d_period',
                 '_stoch_long_threshold', '_stoch_short_threshold')

    def __init__(self, enter_interval: str, exit_interval: str, start_hour: int,
                 end_hour: int, fee: float, enter_k_period: int,
                 enter_smooth: int, enter_d_period: int, exit_k_period: int,
                 exit_smooth: int, exit_d_period: int,
                 stoch_long_threshold=20.0,
                 stoch_short_threshold=80.0):
        super().__init__(enter_interval, exit_interval,
                         start_hour, end_hour, fee)

        # Enter signals stochastic parameters
        self._enter_k_period = enter_k_period
        self._enter_smooth = enter_smooth
        self._enter_d_period = enter_d_period

        self._stoch_long_threshold = stoch_long_threshold
        self._stoch_short_threshold = stoch_short_threshold

        # Exit signals stochastic parameters
        self._exit_k_period = exit_k_period
        self._exit_smooth = exit_smooth
        self._exit_d_period = exit_d_period

    def _calculate_indicators(self):
        """ Applies stochastic oscilator to historical data """
        technical_indicators.StochasticOscillator.apply_full_stochastic_to_df(
            df=self._data,
            k_period=self._enter_k_period,
            smooth=self._enter_smooth,
            d_period=self._enter_d_period)

        technical_indicators.StochasticOscillator.apply_full_stochastic_to_df(
            df=self._exit_df,
            k_period=self._exit_k_period,
            smooth=self._exit_smooth,
            d_period=self._exit_d_period)

        # If strategy is asymetric, fix the datetime index
        if self._enter_interval != self._exit_interval:
            self._exit_df = self._exit_df.reindex(self._data.index).bfill()

        self._data['K_exit'] = self._exit_df['K']
        self._data['D_exit'] = self._exit_df['D']

        del self._exit_df

    def _set_long_positions_logic(self):
        """
        Long position: K line > D line, prev. K < prev. D, K < 20
        Close Long position: exit_K < exit_D, prev. exit_K > prev. exit_D
        """
        self._long_enter_condition = (self._data['K'] > self._data['D']) & \
                                     (self._data['K'].shift(1) < self._data['D'].shift(1)) & \
                                     (self._data['K'] < self._stoch_long_threshold) & \
                                     (self._data['K_exit'] > self._data['D_exit']) & \
                                     (self._data['Hour'] >= self._start_hour) & \
                                     (self._data['Hour'] <= self._end_hour)

        self._long_exit_condition = (self._data['K_exit'] < self._data['D_exit']) & \
                                    (self._data['K_exit'].shift(1) > self._data['D_exit'].shift(1))

    def _set_short_positions_logic(self):
        """
        Short position: K line < D line, prev. K > prev. D, K > 80
        Close Short position: exit_K > exit_D, prev. exit_K < prev. exit_D
        """
        self._short_enter_condition = (self._data['K'] < self._data['D']) & \
                                      (self._data['K'].shift(1) > (self._data['D'].shift(1))) & \
                                      (self._data['K'] > self._stoch_short_threshold) & \
                                      (self._data['K_exit'] < self._data['D_exit']) & \
                                      (self._data['Hour'] >= self._start_hour) & \
                                      (self._data['Hour'] <= self._end_hour)

        self._short_exit_condition = (self._data['K_exit'] > self._data['D_exit']) & \
                                     (self._data['K_exit'].shift(1) < self._data['D_exit'].shift(1))


# import objsize


path = '/Users/kq794tb/Desktop/TRAI_Lite/EURUSD_bid.csv'
strategy = StochasticOscilatorBacktester(
    enter_interval='1T', exit_interval='5T', start_hour=8, end_hour=16,
    fee=0.00015, enter_k_period=14, enter_smooth=3, enter_d_period=3,
    exit_k_period=14, exit_smooth=3, exit_d_period=3, stoch_long_threshold=20,
    stoch_short_threshold=80)

strategy.fit_from_file(path, 'dukascopy')
print(strategy.strategy_return)





