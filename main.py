import datetime
from timeloop import Timeloop

from databases.prices_manager import MongoPricesManager
from databases.ohlc import OHLC
from trading import strategies, broker_api, trading_bot
from price_api import price_api


tl = Timeloop()

broker_auth_path = '/Users/kq794tb/Desktop/TRAI/cmc_markets.txt'
broker_api = broker_api.CMCMarketsAPI(broker_auth_path)

dax_updating = False
dax_prices_list = list()
dax_position = 0
dax_prices_manager = MongoPricesManager('DAX')
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
    short_stoch_threshold=70)

dax_bot = trading_bot.TradingBot(strategy_object=dax_strategy,
                                 broker_api_object=broker_api)

eurusd_updating = False
eurusd_prices_list = list()
eurusd_position = 0
eurusd_prices_manager = MongoPricesManager('EURUSD')
eurusd_api = price_api.PriceAPIFactory.get_price_api(asset='EURUSD')
eurusd_strategy = strategies.StochasticOscillatorStrategy(
    asset='EURUSD',
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
    long_stoch_threshold=20,
    short_stoch_threshold=70)

eurusd_bot = trading_bot.TradingBot(strategy_object=eurusd_strategy,
                                    broker_api_object=broker_api)


@tl.job(interval=datetime.timedelta(milliseconds=100))
def dax_update():
    global dax_updating
    global dax_position

    dax_price = dax_api.get_price()
    if dax_price:
        dax_prices_list.append(dax_price)

    # Execute every full minute
    if datetime.datetime.now().second == 0:
        if not dax_updating:
            dax_updating = True
            ohlc = OHLC.from_prices_list(dax_prices_list)
            dax_prices_manager.insert_ohlc(ohlc)
            tl.logger.info(f'DAX inserted: {ohlc}')

            del dax_prices_list[:]
            dax_position = dax_bot.take_action(dax_position)
    else:
        dax_updating = False


@tl.job(interval=datetime.timedelta(milliseconds=100))
def eurusd_update():
    global eurusd_updating
    global eurusd_position

    eurusd_price = eurusd_api.get_price()
    if eurusd_price:
        eurusd_prices_list.append(eurusd_price)

    # Execute every full minute
    if datetime.datetime.now().second == 0:
        if not eurusd_updating:
            eurusd_updating = True
            ohlc = OHLC.from_prices_list(eurusd_prices_list)
            eurusd_prices_manager.insert_ohlc(ohlc)
            tl.logger.info(f'EURUSD inserted: {ohlc}')

            del eurusd_prices_list[:]
            eurusd_position = eurusd_bot.take_action(eurusd_position)
    else:
        eurusd_updating = False


if __name__ == '__main__':
    tl.start(block=True)
