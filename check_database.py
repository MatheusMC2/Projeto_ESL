import config
import mysql.connector
from datetime import datetime, timedelta

def check_db_gazin(mydb,cursor):
    list_db = []
    query = "SELECT chave_notas FROM python_notas_gazin;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    return list_db

def check_db_kabum(mydb,cursor):
    list_db = []
    query = "SELECT file_name FROM python_notas_kabum;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    return list_db


def check_db_multilaser(mydb,cursor):

    data_now = datetime.today().strftime("%Y-%m-%d")
    past_days = datetime.today() - timedelta(days=30)
    real_date = past_days.strftime("%Y-%m-%d")

    list_db = []
    query = "SELECT file_name FROM python_notas_multilaser ;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    return list_db

def check_db_madesa(mydb,cursor):

    data_now = datetime.today().strftime("%Y-%m-%d")
    past_days = datetime.today() - timedelta(days=30)
    real_date = past_days.strftime("%Y-%m-%d")

    list_db = []
    query = "SELECT file_name FROM python_notas_madesa;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    return list_db

def check_db_madeira():
    mydb = mysql.connector.connect(
        host = config.DATABASE_HOST,
        user = config.DATABASE_USERNAME,
        password = config.DATABASE_PASSWORD,
        database = config.DATABASE_DATABASE
        )
    cursor = mydb.cursor()

    list_db = []
    query = "SELECT chave_notas FROM python_notas_madeira;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    mydb.close()
    return list_db

def check_db_engage(mydb,cursor):

    list_db = []
    query = "SELECT file_name FROM python_notas_engage;" 
    cursor.execute(query)
    result = cursor.fetchall()
    for file in result:
        list_db.append(file[0])
    return list_db



def check_db_mvx(mydb,cursor):
    list_db = []
    query = "SELECT file_name FROM python_notas_mvx"
    cursor.execute(query)
    result = cursor.fetchall()
    for link in result:
        list_db.append(link[0])
    return list_db