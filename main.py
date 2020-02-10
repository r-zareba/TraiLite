import os
import subprocess

print(os.getcwd())
os.chdir('./app_scheduler')
print(os.getcwd())


subprocess.run('celery -A tasks worker --beat --loglevel=info', shell=True)


# import os
# import sys
# import redis
# sys.path.insert(0, './quotations')
#
# import pymongo
#
# import price_api
# import settings

# eurusd_api = price_api.PriceAPIFactory.get_price_api(asset='EURUSD')
# price = eurusd_api.get_price()
#
# print(f'Price : {price}')
# print('Starting MongoDB Client')
#
# mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
#
# print('Mongo client started')
# database = mongo_client['prices']
# collection = database['EURSD']
# #
# ohlc = {'Timestamp': 'ASD',
#         'Price': price}
#
# collection.insert_one(ohlc)


# if settings.ENVIRONMENT == 'MACOS':
#     redis_client = redis.Redis(host='localhost', port=6379)
# else:
#     redis_client = redis.Redis(host='redis', port=6379)
#
# redis_client.set('index', '0')
#
# x = redis_client.get('index')
# for i in range(3):
#     x = redis_client.incr('index')
#
# print(f'Redis value: {x}')

#
# print('document added !')


