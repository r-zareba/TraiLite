import psycopg2
import pandas as pd
from collections import defaultdict

from databases.ohlc import OHLC

from utils import read_config

from databases.postgres.postgres_manager import PostgresManager

db_config = read_config(config_filepath='config.ini', section='postgresql')
postgres_manager = PostgresManager()
postgres_manager.init(db_config)

connection = postgres_manager._connection
cursor = postgres_manager._db_cursor

# sql_statement = """
# SELECT * FROM
# 	(SELECT * FROM prices
# 	WHERE asset = 'EURUSD'
# 	ORDER BY timestamp DESC
# 	LIMIT 4) AS last_prices
# ORDER BY TIMESTAMP;
# """
sql_statement = """
SELECT * FROM
	(SELECT * FROM prices
	WHERE asset = 'EURUSD'
	AND timestamp > '2021-03-25 12:15:00' AND timestamp < '2021-03-25 12::00'
) AS last_prices
ORDER BY TIMESTAMP;
"""

k_period = 14
smooth = 2
d_period = 3

try:
    cursor.execute(sql_statement)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['id', 'timestamp', 'asset', 'Open', 'High', 'Low', 'Close'])

    results = list()
    for row in df.itertuples():
        timestamp = row.timestamp
        results.extend([row.Open, row.High, row.Low, row.Close])




    # low = df['Low'].rolling(window=k_period).min()
    # high = df['High'].rolling(window=k_period).max()
    #
    # k_value = ((df['Close'] - low) / (high - low)) * 100
    # df.loc[:, 'K'] = k_value.rolling(window=smooth).mean()
    # df.loc[:, 'D'] = df['K'].rolling(window=d_period).mean()

    connection.commit()
except Exception as e:
    print(e)
finally:
    postgres_manager.close()

