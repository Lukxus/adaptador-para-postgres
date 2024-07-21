import psycopg2
import logging

class Database:
    def __init__(self, host, dbname, user, password):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        try:
            logging.info("Connecting to the database...")
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.dbname,
                user=self.user,
                password=self.password,
                options="-c client_encoding=UTF8"
            )
            logging.info("Connection successful.")
        except psycopg2.Error as e:
            logging.error(f"Error connecting to the database: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Connection closed.")
