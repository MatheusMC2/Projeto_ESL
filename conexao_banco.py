import config
import mysql.connector

def conexao_banco(x):
    list_db = []
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE
            )
    cursor = mydb.cursor()
    if 'SELECT' in x:
        cursor.execute(x)
        result = cursor.fetchall()
        for file in result:
            list_db.append(file[0])
        return list_db
    else:
        cursor.execute(x)
        mydb.commit()
        mydb.close()