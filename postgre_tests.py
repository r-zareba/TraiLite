import psycopg2

from databases.ohlc import OHLC
from utils import read_config

from databases.postgres.postgres_manager import PostgresManager

db_config = read_config(config_filepath='config.ini', section='postgresql')
postgres_manager = PostgresManager()
postgres_manager.init(db_config)

connection = postgres_manager._connection
cursor = postgres_manager._db_cursor

insert_statement = """
INSERT INTO prices (currency, open, high, low, close) VALUES (%s, %s, %s, %s, %s) RETURNING id;
"""

try:
    ohlc = OHLC.from_prices_list([1.1111, 1.1122, 1.1132])
    postgres_manager.insert_ohlc('DAX', ohlc)



    # cursor.execute(insert_statement, ('EURUSD', 1.1192, 1.1111, 1.1100, 1.1212, ))
    # # fetched = cursor.fetchone()
    # # print(f'FETCHED : {fetched}')
    connection.commit()
except Exception as e:
    print(e)
finally:
    postgres_manager.close()
