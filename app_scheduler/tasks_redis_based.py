import celery
import pymongo
import datetime as dt

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

import redis


app = celery.Celery('tasks')
app.config_from_object('tasks_config')
redis_client = redis.Redis()


# Redis Lock decorator for celery tasks
def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""
    def _dec(run_func):
        """Decorator."""
        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            lock = redis_client.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()
            return ret_value
        return _caller
    return _dec(function) if function is not None else _dec


eurusd_api = price_api.PriceAPIFactory(asset='EURUSD').get_price_api()


class ReadEURUSD(app.Task):
    """A task."""

    @only_one(key='ReadEURUSD', timeout=60 * 5)
    def run(self, **kwargs):
        # Append some data to redis list
        redis_client.rpush('EURUSD', eurusd_api.get_price())


class EURUSDAction(app.Task):
    """A task."""

    # Database connection instance shared between worker
    # See https://docs.celeryproject.org/en/latest/userguide/tasks.html
    _mongo_client = None

    @property
    def mongo_client(self):
        if self._mongo_client is None:
            self._mongo_client = pymongo.MongoClient()
        return self._mongo_client

    @only_one(key='EURUSDAction', timeout=60 * 5)
    def run(self, **kwargs):

        # Read current list of sensor values from Redis
        current_sensor_values = redis_client.lrange('EURUSD', 0, -1)

        # Convert Redis list to python float list
        # map compares to list comprehension is a bit faster in my case
        # values = [float(i) for i in current_sensor_values]
        values = list(map(float, current_sensor_values))

        shifted_time = dt.datetime.now() - dt.timedelta(minutes=1)
        ohlc = {'Timestamp': shifted_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Open': values[0],
                'High': max(values),
                'Low': min(values),
                'Close': values[-1]}

        # Insert document to Mongo database and clean the Redis list
        self.mongo_client['prices']['EURUSD'].insert_one(ohlc)
        redis_client.delete('EURUSD')


read_eurusd = app.register_task(ReadEURUSD())
eurusd_action = app.register_task(EURUSDAction())