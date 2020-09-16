import abc
from datetime import datetime as dt

from . import indicators_readers


class BaseStrategy:
    """
    Implementation of Strategies Abstract class
    Contains logic for making transactions
    """
    __slots__ = ('_asset', '_enter_interval', '_exit_interval', '_start_hour',
                 '_end_hour', '_indicator_reader', '_enter_minute',
                 '_exit_minute')

    def __init__(self, asset: str, enter_interval: str, exit_interval: str,
                 start_hour: int, end_hour: int) -> None:
        self._asset = asset
        self._enter_interval = enter_interval
        self._exit_interval = exit_interval
        self._start_hour = start_hour
        self._end_hour = end_hour

        self._indicator_reader: indicators_readers.BaseIndicatorReader = None

        self._enter_minute = indicators_readers.n_minutes_dict[enter_interval]
        self._exit_minute = indicators_readers.n_minutes_dict[exit_interval]

    @property
    def asset(self) -> str:
        return self._asset

    def _check_enter_interval(self) -> bool:
        current_minute = dt.now().minute
        return current_minute % self._enter_minute == 0

    def _check_exit_interval(self) -> bool:
        current_minute = dt.now().minute
        return current_minute % self._exit_minute == 0

    @abc.abstractmethod
    def _got_take_long_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def _got_close_long_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def _got_take_short_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def _got_close_short_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def get_action(self, current_position: int) -> int:
        pass


class StochasticOscillatorStrategy(BaseStrategy):

    __slots__ = ('_enter_k_period', '_enter_smooth', '_enter_d_period',
                 '_exit_k_period', '_exit_smooth', '_exit_d_period',
                 '_long_stoch_threshold', '_short_stoch_threshold')

    def __init__(
            self, asset: str, enter_interval: str, exit_interval: str,
            start_hour: int, end_hour: int, enter_k_period: int,
            enter_smooth: int, enter_d_period: int, exit_k_period: int,
            exit_smooth: int, exit_d_period: int, long_stoch_threshold: float,
            short_stoch_threshold: float) -> None:

        super().__init__(asset, enter_interval, exit_interval,
                         start_hour, end_hour)

        self._enter_k_period = enter_k_period
        self._enter_smooth = enter_smooth
        self._enter_d_period = enter_d_period
        self._exit_k_period = exit_k_period
        self._exit_smooth = exit_smooth
        self._exit_d_period = exit_d_period
        self._long_stoch_threshold = long_stoch_threshold
        self._short_stoch_threshold = short_stoch_threshold

    def _got_take_long_signal(self) -> bool:
        return (self._indicator_reader.current_enter_k >
                self._indicator_reader.current_enter_d) & \
               (self._indicator_reader.previous_enter_k <
                self._indicator_reader.previous_enter_d) & \
               (self._indicator_reader.current_exit_k >
                self._indicator_reader.current_exit_d) & \
               (self._indicator_reader.current_enter_k <
                self._long_stoch_threshold) & \
               (self._indicator_reader.hour >= self._start_hour) & \
               (self._indicator_reader.hour <= self._end_hour)

    def _got_close_long_signal(self) -> bool:
        return (self._indicator_reader.current_exit_k <
                self._indicator_reader.current_exit_d) & \
               (self._indicator_reader.previous_exit_k >
                self._indicator_reader.previous_exit_d)

    def _got_take_short_signal(self) -> bool:
        return (self._indicator_reader.current_enter_k <
                self._indicator_reader.current_enter_d) & \
               (self._indicator_reader.previous_enter_k >
                self._indicator_reader.previous_enter_d) & \
               (self._indicator_reader.current_exit_k <
                self._indicator_reader.current_exit_d) & \
               (self._indicator_reader.current_enter_k >
                self._short_stoch_threshold) & \
               (self._indicator_reader.hour >= self._start_hour) & \
               (self._indicator_reader.hour <= self._end_hour)

    def _got_close_short_signal(self) -> bool:
        return (self._indicator_reader.current_exit_k >
                self._indicator_reader.current_exit_d) & \
               (self._indicator_reader.previous_exit_k <
                self._indicator_reader.previous_exit_d)

    def get_action(self, current_position: int) -> int:
        """
        Checks actual strategy signals based on current position and
        returns action 1 - long or -1 - short for broker API
        In case when no signal was detected - returns 0 (no action)
        """
        self._indicator_reader = indicators_readers.StochasticOscillatorReader(
            self._asset, self._enter_interval, self._exit_interval,
            self._enter_k_period, self._enter_smooth, self._enter_d_period,
            self._exit_k_period, self._exit_smooth, self._exit_d_period)

        self._indicator_reader.update_indicators()

        if not self._indicator_reader.are_indicators_calculated:
            return 0

        if current_position == 0 and self._check_enter_interval():
            if self._got_take_long_signal():
                return 1
            elif self._got_take_short_signal():
                return -1

        elif current_position == 1 and self._check_exit_interval():
            if self._got_close_long_signal():
                return -1

        elif current_position == -1 and self._check_exit_interval():
            if self._got_close_short_signal():
                return 1
        return 0
