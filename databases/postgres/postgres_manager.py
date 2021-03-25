import os
import psycopg2

from databases.ohlc import OHLC


class PostgresManager:

    INIT_SQL_PATH = os.path.join('databases', 'postgres', 'db_init.sql')
    INSERT_OHLC_SQL = """
        INSERT INTO prices (timestamp, currency, open, high, low, close)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    def __init__(self):
        self._connection = None
        self._db_cursor = None

    def init(self, db_config: dict):
        print(f'Connecting to PostgreSQL...')

        try:
            self._connection = psycopg2.connect(**db_config)
            self._db_cursor = self._connection.cursor()
        except (Exception, psycopg2.DatabaseError) as e:
            print(f'Cannot connect to PostgreSQL: {e}')

        self._db_cursor.execute('SELECT version()')
        version = self._db_cursor.fetchone()
        print(f'Sucessfully connected to: {version}\nPreparing database schemas...')

        with open(self.INIT_SQL_PATH) as f:
            initial_schema_sql_statement = f.read()

        self._db_cursor.execute(initial_schema_sql_statement)
        self._connection.commit()
        print('Schemas initialized sucessfully')

    def close(self):
        print(f'\nClosing PostgreSQL connection...')
        self._db_cursor.close()
        self._connection.close()
        print(f'PostgreSQL connection closed')

    def insert_ohlc(self, asset: str, ohlc: OHLC):
        self._db_cursor.execute(
            self.INSERT_OHLC_SQL, (ohlc.timestamp, asset, ohlc.open, ohlc.high, ohlc.low, ohlc.close, ))
        self._connection.commit()








