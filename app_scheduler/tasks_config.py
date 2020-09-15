from celery.schedules import crontab
import sys
sys.path.insert(0, '../')

import settings


# if settings.ENVIRONMENT == 'MACOS':
#     broker_url = 'redis://localhost:6379/0'
#     result_backend = 'redis://localhost:6379/0'
# else:
#     broker_url = 'redis://redis:6379/0'
#     result_backend = 'redis://redis:6379/0'


if settings.ENVIRONMENT == 'MACOS':
    broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'
    result_backend = 'amqp://myuser:mypassword@localhost:5672/myvhost'
else:
    broker_url = 'amqp://admin:pass@rabbit:5672'
    result_backend = 'rpc://admin:pass@rabbit:5672'


task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Warsaw'
enable_utc = True

""" Periodic tasks """
beat_schedule = {

    # Updating prices
    'update-eurusd': {
        'task': 'tasks.update_eurusd',
        'schedule': 0.100,  # 100 milliseconds
        # 'args': ()
    },

    'update-dax': {
        'task': 'tasks.update_dax',
        'schedule': 0.100,
    },
    #
    # 'update-gbpusd': {
    #     'task': 'tasks.update_gbpusd',
    #     'schedule': 0.250,
    # },


    # Actions
    'eurusd-action': {
        'task': 'tasks.EURUSDAction',
        'schedule': crontab(minute='*/1')
    },

    'dax-action': {
        'task': 'tasks.DAXAction',
        'schedule': crontab(minute='*/1')
    },
    #
    # 'gbpusd-action': {
    #     'task': 'tasks.GBPUSDAction',
    #     'schedule': crontab(minute='*/1')
    # },

}

# TODO task queues based on users
# task_routes = {'tasks.update_eurusd': {'queue': 'update_eurusd'},
#                'tasks.eurusd_action': {'queue': 'eurusd_action'},
#                'tasks.update_dax': {'queue': 'update_dax'},
#                'tasks.dax_action': {'queue': 'dax_action'}}
