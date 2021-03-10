import datetime
from timeloop import Timeloop

from databases.mongo.mongo_manager import MongoPricesManager, MongoTransactionsManager, MongoStochasticIndicatorManager
from databases.ohlc import OHLC, Color
from trading import strategies, broker_api, trading_bot
from price_api import price_api
from settings import MONGO_HOST

""" 
Important note:
Meant to run in a single process (multithreaded)
No locks required
"""

MAX_RETRIES = 3
PRICE_READ_INTERVAL = 100  # milliseconds

tl = Timeloop()

broker_auth_path = '/Users/kq794tb/Desktop/TRAI/cmc_markets.txt'
broker_api = broker_api.CMCMarketsAPI(broker_auth_path)
prices_manager = MongoPricesManager(MONGO_HOST)
transactions_manager = MongoTransactionsManager(MONGO_HOST)
stochastic_manager = MongoStochasticIndicatorManager(MONGO_HOST)
prices_printed = False

dax_updating = False
dax_prices_list = list()
dax_position = transactions_manager.get_current_position('DAX')
dax_n_times_restarted = 0
dax_api = price_api.PriceAPIFactory.get_price_api(asset='DAX')
dax_strategy = strategies.StochasticOscillatorStrategy(
    asset='DAX',
    enter_interval='1T',
    exit_interval='15T',
    start_hour=7,
    end_hour=16,
    enter_k_period=7,
    enter_smooth=2,
    enter_d_period=2,
    exit_k_period=12,
    exit_smooth=2,
    exit_d_period=2,
    long_stoch_threshold=29,
    short_stoch_threshold=70,
    prices_manager=prices_manager,
    indicator_manager=stochastic_manager)

dax_bot = trading_bot.TradingBot(strategy_object=dax_strategy,
                                 broker_api_object=broker_api,
                                 transactions_manager=transactions_manager)

eurusd_updating = False
eurusd_prices_list = list()
eurusd_position = transactions_manager.get_current_position('EURUSD')
eurusd_n_times_restarted = 0
eurusd_api = price_api.PriceAPIFactory.get_price_api(asset='EURUSD')
eurusd_strategy = strategies.StochasticOscillatorStrategy(
    asset='EURUSD',
    enter_interval='1T',
    exit_interval='5T',
    start_hour=7,
    end_hour=16,
    enter_k_period=7,
    enter_smooth=2,
    enter_d_period=2,
    exit_k_period=12,
    exit_smooth=2,
    exit_d_period=2,
    long_stoch_threshold=20,
    short_stoch_threshold=70,
    prices_manager=prices_manager,
    indicator_manager=stochastic_manager)

eurusd_bot = trading_bot.TradingBot(strategy_object=eurusd_strategy,
                                    broker_api_object=broker_api,
                                    transactions_manager=transactions_manager)

gbpusd_updating = False
gbpusd_prices_list = list()
gbpusd_position = transactions_manager.get_current_position('GBPUSD')
gbpusd_n_times_restarted = 0
gbpusd_api = price_api.PriceAPIFactory.get_price_api(asset='GBPUSD')
gbpusd_strategy = strategies.StochasticExtendedStrategy(
    asset='GBPUSD',
    enter_interval='5T',
    exit_interval='5T',
    start_hour=7,
    end_hour=16,
    enter_k_period=7,
    enter_smooth=2,
    enter_d_period=2,
    exit_k_period=12,
    exit_smooth=2,
    exit_d_period=2,
    long_stoch_threshold=25,
    short_stoch_threshold=70,
    prices_manager=prices_manager,
    indicator_manager=stochastic_manager)

gbpusd_bot = trading_bot.TradingBot(strategy_object=gbpusd_strategy,
                                    broker_api_object=broker_api,
                                    transactions_manager=transactions_manager)

"""
Register periodic tasks
"""


@tl.job(interval=datetime.timedelta(milliseconds=PRICE_READ_INTERVAL))
def dax_update():
    global dax_updating
    global dax_position
    global dax_api
    global dax_n_times_restarted
    global prices_printed

    try:
        dax_price = dax_api.get_price()
    except Exception as e:
        if dax_n_times_restarted < MAX_RETRIES:
            tl.logger.error(f'DAX price api error: {e}\nRestarting...')
            dax_api.restart()
            dax_n_times_restarted += 1
    else:
        if dax_price:
            dax_prices_list.append(dax_price)
        dax_n_times_restarted = 0

    if dax_n_times_restarted >= MAX_RETRIES:
        # TODO Send email / sms / notification
        return

    # Execute every full minute
    if datetime.datetime.now().second == 0:
        if not dax_updating:
            dax_updating = True
            ohlc = OHLC.from_prices_list(dax_prices_list, Color.GREEN)
            prices_manager.insert_ohlc(ohlc, 'DAX')
            if not prices_printed:
                prices_printed = True
                tl.logger.info(f'{Color.UNDERLINE}{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Color.END} :')
            tl.logger.info(f'DAX inserted: {ohlc}')

            del dax_prices_list[:]
            dax_position = dax_bot.take_action(dax_position)
    else:
        dax_updating = False
        prices_printed = False


@tl.job(interval=datetime.timedelta(milliseconds=PRICE_READ_INTERVAL))
def eurusd_update():
    global eurusd_updating
    global eurusd_position
    global eurusd_api
    global eurusd_n_times_restarted
    global prices_printed

    try:
        eurusd_price = eurusd_api.get_price()
    except Exception as e:
        if eurusd_n_times_restarted < MAX_RETRIES:
            tl.logger.error(f'EURUSD price api error: {e}\nRestarting...')
            eurusd_api.restart()
            eurusd_n_times_restarted += 1
    else:
        if eurusd_price:
            eurusd_prices_list.append(eurusd_price)
        eurusd_n_times_restarted = 0

    if eurusd_n_times_restarted >= MAX_RETRIES:
        # TODO Send email / sms / notification
        return

    # Execute every full minute
    if datetime.datetime.now().second == 0:
        if not eurusd_updating:
            eurusd_updating = True
            ohlc = OHLC.from_prices_list(eurusd_prices_list, Color.YELLOW)
            prices_manager.insert_ohlc(ohlc, 'EURUSD')
            if not prices_printed:
                prices_printed = True
                tl.logger.info(f'{Color.UNDERLINE}{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Color.END} :')
            tl.logger.info(f'EURUSD inserted: {ohlc}')

            del eurusd_prices_list[:]
            eurusd_position = eurusd_bot.take_action(eurusd_position)
    else:
        eurusd_updating = False
        prices_printed = False


@tl.job(interval=datetime.timedelta(milliseconds=PRICE_READ_INTERVAL))
def gbpusd_update():
    global gbpusd_updating
    global gbpusd_position
    global gbpusd_api
    global gbpusd_n_times_restarted
    global prices_printed

    try:
        gbpusd_price = gbpusd_api.get_price()
    except Exception as e:
        if gbpusd_n_times_restarted < MAX_RETRIES:
            tl.logger.error(f'GBPUSD price api error: {e}\nRestarting...')
            gbpusd_api.restart()
            gbpusd_n_times_restarted += 1
    else:
        if gbpusd_price:
            gbpusd_prices_list.append(gbpusd_price)
        gbpusd_n_times_restarted = 0

    if gbpusd_n_times_restarted >= MAX_RETRIES:
        # TODO Send email / sms / notification
        return

    # Execute every full minute
    if datetime.datetime.now().second == 0:
        if not gbpusd_updating:
            gbpusd_updating = True
            ohlc = OHLC.from_prices_list(gbpusd_prices_list, Color.RED)
            prices_manager.insert_ohlc(ohlc, 'GBPUSD')

            if not prices_printed:
                prices_printed = True
                tl.logger.info(f'{Color.UNDERLINE}{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Color.END} :')
            tl.logger.info(f'GBPUSD inserted: {ohlc}')

            del gbpusd_prices_list[:]
            gbpusd_position = gbpusd_bot.take_action(gbpusd_position)
    else:
        gbpusd_updating = False
        prices_printed = False


# TODO
@tl.job(interval=datetime.timedelta(minutes=5))
def check_internet_connection():
    global dax_n_times_restarted
    global eurusd_n_times_restarted
    global gbpusd_n_times_restarted

    dax_n_times_restarted = 0
    eurusd_n_times_restarted = 0
    gbpusd_n_times_restarted = 0


if __name__ == '__main__':
    tl.start(block=True)
