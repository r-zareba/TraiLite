import celery
import multiprocessing
from datetime import datetime as dt

import sys
sys.path.insert(0, '../databases')
sys.path.insert(0, '../trading')
sys.path.insert(0, '../quotations')
import tasks_config
import mongo_manager
import strategies
import broker_api
import trading_bot
import price_api


broker_auth_path = '/Users/kq794tb/Desktop/TRAI/cmc_markets.txt'


""" Initialize Celery app """
app = celery.Celery('tasks')
app.config_from_object('tasks_config')


""" Define shared attributes for all Celery workers """
manager = multiprocessing.Manager()

eurusd_shared_list = manager.list()
# dax_shared_list = manager.list()
# gbpusd_shared_list = manager.list()

eurusd_position = multiprocessing.Value('i', 0)
# dax_position = multiprocessing.Value('i', 0)
# gbpusd_position = multiprocessing.Value('i', 0)


""" Trading Bots initialization """
eurusd_api = price_api.PriceAPIFactory.get_price_api(asset='EURUSD')
# dax_api = price_api.PriceAPIFactory.get_price_api(asset='DAX')
# gbpusd_api = price_api.PriceAPIFactory.get_price_api(asset='GBPUSD')

eurusd_strategy = strategies.StochasticOscillatorStrategy(
    asset='EURUSD',
    enter_interval='1T',
    exit_interval='1T',
    start_hour=7,
    end_hour=17,
    enter_k_period=14,
    enter_smooth=3,
    enter_d_period=3,
    exit_k_period=14,
    exit_smooth=3,
    exit_d_period=3,
    long_stoch_threshold=20,
    short_stoch_threshold=80)

# dax_strategy = strategies.StochasticOscillatorStrategy(
#     asset='DAX',
#     enter_interval='5T',
#     exit_interval='5T',
#     start_hour=7,
#     end_hour=17,
#     enter_k_period=7,
#     enter_smooth=3,
#     enter_d_period=3,
#     exit_k_period=7,
#     exit_smooth=3,
#     exit_d_period=3,
#     long_stoch_threshold=20,
#     short_stoch_threshold=80)
#
# gbpusd_strategy = strategies.StochasticOscillatorStrategy(
#     asset='GBPUSD',
#     enter_interval='1T',
#     exit_interval='5T',
#     start_hour=7,
#     end_hour=17,
#     enter_k_period=7,
#     enter_smooth=3,
#     enter_d_period=3,
#     exit_k_period=7,
#     exit_smooth=3,
#     exit_d_period=3,
#     long_stoch_threshold=20,
#     short_stoch_threshold=80)

broker_api = broker_api.CMCMarketsAPI(broker_auth_path)

eurusd_logger = mongo_manager.MongoTransactionLogger('EURUSD')

eurusd_bot = trading_bot.TradingBot(strategy_object=eurusd_strategy,
                                    broker_api_object=broker_api,
                                    transaction_logger=eurusd_logger)
# dax_bot = trading_bot.TradingBot(strategy_object=dax_strategy,
#                                  broker_api_object=broker_api)
# gbpusd_bot = trading_bot.TradingBot(strategy_object=gbpusd_strategy,
#                                     broker_api_object=broker_api)


""" Updating prices list - occures every 250 miliseconds """
@app.task(ignore_result=True)
def update_eurusd() -> None:
    eurusd_shared_list.append(eurusd_api.get_price())


# @app.task(ignore_result=True)
# def update_dax() -> None:
#     dax_shared_list.append(dax_api.get_price())
#
#
# @app.task(ignore_result=True)
# def update_gbpusd() -> None:
#     gbpusd_shared_list.append(gbpusd_api.get_price())


"""
Actions - occures every minute
Inserting OHLC to mongoDB, take trading bot action
"""


class EURUSDAction(app.Task):
    """A task."""
    # Database connection instance shared between workers
    # See https://docs.celeryproject.org/en/latest/userguide/tasks.html
    _mongo_writer = None

    @property
    def mongo_writer(self):
        if self._mongo_writer is None:
            self._mongo_writer = mongo_manager.MongoPricesWriter('EURUSD')
        return self._mongo_writer

    def run(self):
        if eurusd_shared_list:
            self.mongo_writer.insert_ohlc(shared_list=eurusd_shared_list)
            del eurusd_shared_list[:]

            with eurusd_position.get_lock():
                eurusd_position.value = eurusd_bot.take_action(
                    eurusd_position.value)


# class DAXAction(app.Task):
#     _mongo_writer = None
#
#     @property
#     def mongo_writer(self):
#         if self._mongo_writer is None:
#             self._mongo_writer = mongo_manager.MongoPricesWriter('DAX')
#         return self._mongo_writer
#
#     def run(self):
#         if dax_shared_list:
#             self.mongo_writer.insert_ohlc(shared_list=dax_shared_list)
#             del dax_shared_list[:]
#
#             with dax_position.get_lock():
#                 dax_position.value = dax_bot.take_action(dax_position.value)
#
#
# class GBPUSDAction(app.Task):
#     _mongo_writer = None
#
#     @property
#     def mongo_writer(self):
#         if self._mongo_writer is None:
#             self._mongo_writer = mongo_manager.MongoPricesWriter('GBPUSD')
#         return self._mongo_writer
#
#     def run(self):
#         if gbpusd_shared_list:
#             self.mongo_writer.insert_ohlc(shared_list=gbpusd_shared_list)
#             del gbpusd_shared_list[:]
#
#             with gbpusd_position.get_lock():
#                 gbpusd_position.value = gbpusd_bot.take_action(
#                     gbpusd_position.value)


""" Register Celery action tasks for workers """
eurusd_action = app.register_task(EURUSDAction())
# dax_action = app.register_task(DAXAction())
# gbpusd_action = app.register_task(GBPUSDAction())
