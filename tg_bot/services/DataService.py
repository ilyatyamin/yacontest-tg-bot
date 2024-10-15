import datetime

import psycopg2
import logging
import time


class DataService:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.__connection = None

        is_connected = False
        for attempt in range(5):
            try:
                # connect to database
                self.__connection = psycopg2.connect(
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port,
                )
                logging.info("Connection to PostgreSQL DB successful")

                self.__connection.autocommit = True
                self.__create_table_if_not_exists()
                is_connected = True

                break

            except Exception as e:
                logging.error("Problem with connection to database. try again...")
                time.sleep(3)
        if not is_connected:
            raise Exception("No connection to DB... exit")

    def __del__(self):
        self.__connection.close()
        logging.info("Connection to PostgreSQL DB closed.")

    def insert_new_response(self, tg_id, response_time: datetime.datetime,
                            contest_id: str, attempt_id: str, test_id: str):
        cursor = self.__connection.cursor()
        query = f"""
        insert into user_requests_bot values (
        DEFAULT, %s, %s, %s, %s, %s
        )
        """

        cursor.execute(query, (str(tg_id), str(self.__datetime_to_postgres(response_time)),
                               str(contest_id), str(attempt_id), str(test_id)))

        self.__connection.commit()
        logging.info(f"Inserted in the table new response, response_time = {response_time}, tg_id = {tg_id}")

    def count_user_responses(self, tg_id: str, time_from: datetime.datetime = None,
                             time_to: datetime.datetime = None):

        str_from = self.__datetime_to_postgres(time_from)
        str_to = self.__datetime_to_postgres(time_to)

        cursor = self.__connection.cursor()

        query = """
            SELECT COUNT(*)
            FROM user_requests_bot us
            WHERE us.telegram_id = %s 
        """

        params = [tg_id]
        if time_from is not None:
            query += " AND us.response_time >= %s"
            params.append(str_from)

        if time_to is not None:
            if time_from is None:
                query += " AND us.response_time <= %s"
            else:
                query += " AND us.response_time <= %s"
            params.append(str_to)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        self.__connection.commit()
        logging.info(f"Counted user responses: {count}.")

        return count


    def __create_table_if_not_exists(self):
        cursor = self.__connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_requests_bot (
        id serial PRIMARY KEY ,
        telegram_id VARCHAR(50) NOT NULL,
        response_time TIMESTAMP NOT NULL,
        contest_id VARCHAR(50) NOT NULL,
        attempt_id VARCHAR(50) NOT NULL,
        test_id VARCHAR(50) NOT NULL
        );
        """)
        self.__connection.commit()

    @staticmethod
    def __datetime_to_postgres(datetime_obj: datetime.datetime):
        if datetime_obj is not None:
            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        return None
