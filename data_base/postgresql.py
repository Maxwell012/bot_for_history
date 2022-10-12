import psycopg2
from psycopg2 import pool

from create_logger import create_logger


#######################################################################################################################


logger_db = create_logger(__name__)

class Database:
    def __init__(self, db_uri):
        self.pool = psycopg2.pool.ThreadedConnectionPool(2, 10, db_uri)

    def create_connection(self):
        connection = self.pool.getconn()
        return connection

    @staticmethod
    async def db_check_id(id, connection):
        try:
            sql = "SELECT id FROM users WHERE id=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [id])
                check_id = cursor.fetchall()
                if check_id:
                    return check_id
                return None
        except:
            logger_db.critical('db_check_id', exc_info=True)

    @classmethod
    async def db_add_data(cls, id, data, connection):
        try:
            with connection.cursor() as cursor:
                if await cls.db_check_id(id, connection):
                    sql = "UPDATE users SET surname=%s, email=%s, time=%s, incorrect_answer=%s " \
                          "WHERE id=%s"
                    cursor.execute(sql, [data['surname'],
                                         data['email'],
                                         data['time'],
                                         data['incorrect_answer'],
                                         id])
                else:
                    sql = "INSERT INTO users(id, surname, email, time, incorrect_answer) " \
                          "VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, [id,
                                         data['surname'],
                                         data['email'],
                                         data['time'],
                                         data['incorrect_answer']])
                connection.commit()
        except:
            logger_db.critical('db_add_data', exc_info=True)
    @staticmethod
    async def db_get_amount_test(id, connection):
        try:
            sql = "SELECT free_test FROM users WHERE id=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [id])
                amount = cursor.fetchall()
            if amount:
                return amount[0][0]
            else:
                return 0
        except:
            logger_db.critical('db_get_amount_free_test', exc_info=True)

    @staticmethod
    async def db_get_data(id, connection):
        try:
            sql = "SELECT surname, email, time, incorrect_answer " \
                  "FROM users WHERE id=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [id])
                data = cursor.fetchall()
            if data:
                return data[0]
            else:
                return 0
        except:
            logger_db.critical('db_get_data', exc_info=True)

    @classmethod
    async def db_async_update_amount_test(cls, id, amount, connection):
        try:
            amount_test_now = await cls.db_get_amount_test(id, connection)
            amount += amount_test_now
            sql = "UPDATE users SET free_test=%s WHERE id=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [amount, id])
                connection.commit()
        except:
            logger_db.critical('add_test', exc_info=True)

    @staticmethod
    async def db_get_ids(connection):
        try:
            sql = "SELECT id FROM users"
            with connection.cursor() as cursor:
                ids = cursor.fetchall(sql)
            return ids
        except:
            logger_db.critical('get_all_id', exc_info=True)

    @staticmethod
    def db_sync_update_amount_test(id, connection):
        try:
            sql = "SELECT free_test FROM users WHERE id=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql, [id])
                amount = cursor.fetchall()[0][0]
                amount += 1
                sql = "UPDATE users SET free_test=%s WHERE id=%s"
                cursor.execute(sql, [amount, id])
                connection.commit()
        except:
            logger_db.critical('db_update_free_test', exc_info=True)