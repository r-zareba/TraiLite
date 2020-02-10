import datetime

import broker_api
import strategies

import sys
sys.path.insert(0, '../databases')
import mongo_manager


class TradingBot:
    """
    Implementation of fully automated trading bot
    It needs to be initialized with strategy and broker api objects

    take_action - periodic tasks that should be handled by asynchrounous
    agent - Celery by default
    """
    __slots__ = ('_asset', '_strategy_object', '_broker_api_object',
                 '_transactions_logger', '_current_position', '_position_size',
                 '_is_broker_api_initialized')

    def __init__(self, strategy_object: strategies.BaseStrategy,
                 broker_api_object: broker_api.BaseBrokerAPI):

        self._strategy_object = strategy_object
        self._asset = self._strategy_object.asset
        self._broker_api_object = broker_api_object

        # TODO
        self._position_size: int = 100

        # TODO Temporary for tests
        self._broker_api_object.is_ready = True

    def take_action(self, current_position: int) -> int:
        """
        Takes trading action based on current position taken and strategy signal
        :param current_position: 0 - no position, -1 - short or 1 - long
        :return: action taken : 0, -1 or 1
        """
        if not self._broker_api_object.is_ready:
            return 0

        action = self._strategy_object.get_action(current_position)

        if action == 1:
            # self._broker_api_object.go_long(self._position_size) TODO
            if current_position == 0:
                self._log_action(action=action, comment='Long')
                return 1

            self._log_action(action=action, comment='Closing Short')
            return 0

        elif action == -1:
            # self._broker_api_object.go_short(self._position_size) TODO
            if current_position == 0:
                self._log_action(action=action, comment='Short')
                return -1

            self._log_action(action=action, comment='Closing Long')
            return 0

        return current_position

    def _log_action(self, action: int, comment: str) -> None:
        tx_logger = mongo_manager.MongoTransactionsLogger(self._asset)
        tx_logger.log(action=action, comment=comment)
