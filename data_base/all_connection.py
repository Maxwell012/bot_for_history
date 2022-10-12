from data_base.postgresql import Database

from config import db_uri

db = Database(db_uri)
main_thread_connection = db.create_connection()
thread_connection = db.create_connection()