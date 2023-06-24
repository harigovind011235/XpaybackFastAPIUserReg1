import psycopg2
from pymongo import MongoClient

PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "userDb"
PG_USER = ""
PG_PASSWORD = ""

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "userPicsDb"


def get_postgresql_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        return conn

    except Exception as e:
        print("Error in postgres connection -> {}".format(e))


def get_mongodb_connection():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DATABASE]
        return db

    except Exception as e:
        print("Error in mongodb connection -> {}".format(e))