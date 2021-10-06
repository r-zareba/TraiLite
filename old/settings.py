import os

ENVIRONMENT = os.environ.get('ENVIRONMENT')

if ENVIRONMENT == 'MACOS':
    MONGO_HOST = 'mongodb://localhost:27017/'
else:
    MONGO_HOST = 'mongodb://db:27017/'
