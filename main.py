# import os
# import subprocess
#
# print(os.getcwd())
# os.chdir('./app_scheduler')
# print(os.getcwd())
#
#
# subprocess.run('celery -A tasks worker --beat --loglevel=info', shell=True)
#

import os
import sys
sys.path.insert(0, './quotations')

import price_api




# eurusd_api = price_api.PriceAPIFactory.get_price_api(asset='EURUSD')
