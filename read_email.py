import re
import config
import ftplib
import requests
import pandas as pd
import check_database
import mysql.connector
import read_pdf
from io import BytesIO
from zipfile2 import ZipFile
from imap_tools import MailBox, AND
from datetime import date, datetime, timedelta

#função para identificar o arquivo da nota
def confirm_pdf_nota(string):
    name = r'^\d+\.(pdf|PDF)$'
    if re.search(name, string):
        return True
    else:
        return False

#função para idantificar o arquivo zip
def confirm_file_zip(string):
    name = r'(NFe_PDF\.zip)'
    if re.search(name, string):
        return True
    else:
        return False

#função para ler os emails, atualizar o ftp e o banco
def read_email_kabum():
    print('---------------- Baixando notas dos e-mails da Kabum ----------------')

     #conexão com o banco de dados
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE
            )
    cursor = mydb.cursor()

    conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA,config.USERNAME_CONECTA,config.PASSWORD_CONECTA)
    
    today = date.today()
    past_days = date.today() - timedelta(3)

    email_client = MailBox(config.email_imap).login(config.email_user, config.email_password)
    list_emails = email_client.fetch(AND(from_= config.email_from_kabum, date_gte= past_days, date_lt=today), reverse=True)

    list_db = check_database.check_db_kabum(mydb= mydb, cursor= cursor)

    for email_client in list_emails:

        if len(email_client.attachments) > 0:
            for anexo in email_client.attachments:

                try:
                   if confirm_pdf_nota(anexo.filename):
                        if anexo.filename in list_db:
                            print(f'O arquivo {anexo.filename} ja foi baixado')
                            continue
                        else:
                            pdf_bytes = anexo.payload
                            file_pdf = BytesIO(pdf_bytes)

                            path_save = config.PATH_DANF_KABUM + anexo.filename
                            conecta_ftp.storbinary('STOR ' + path_save, file_pdf)
                            file_pdf = None #Limpa o conteudo da variavel
                            print(f'O arquivo: {anexo.filename} foi salvo')
                            query = "INSERT INTO python_notas_kabum (file_name, upload_date, email_date) VALUES ('" + anexo.filename + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', '" + email_client.date.strftime("%Y-%m-%d %H:%M:%S") + "');" 
                            cursor.execute(query)
                            mydb.commit()
                except Exception as e:
                    print(e)
    conecta_ftp.quit()
    mydb.close()


#função para ler os emails, atualizar o ftp e o banco
def read_email_multilaser():
    print('---------------- Baixando notas dos e-mails da Multilaser ----------------')
    
     #conexão com o banco de dados
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE
            )
    cursor = mydb.cursor()

    conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA,config.USERNAME_CONECTA,config.PASSWORD_CONECTA)
    
    today = date.today()
    past_days = date.today() - timedelta(3)

    email_client = MailBox(config.email_imap).login(config.email_user, config.email_password)
    list_emails = email_client.fetch(AND(from_= config.email_from_multilaser, date_gte= past_days, date_lt=today), reverse=True)

    list_db = check_database.check_db_multilaser(mydb= mydb, cursor= cursor)

    for email_client in list_emails:
      
        if len(email_client.attachments) > 0:
            for anexo in email_client.attachments:
                    
                if confirm_file_zip(anexo.filename):
                    print(f'Lendo arquivo {anexo.filename}')
                    zip_bytes = anexo.payload
                    file_zip = BytesIO(zip_bytes)

                    with ZipFile(file_zip, 'r') as zf:

                        pdf_notas = [file for file in zf.namelist() if file.endswith('.pdf')]
                        print('-------------- Notas encontradas --------------')
                        for nota in pdf_notas:
                            if nota not in list_db:
                                
                                with zf.open(nota) as nota:
                                    save_nota = nota.read()
                                    file_pdf = BytesIO(save_nota)

                                    path_save = config.PATH_DANF_MULTILASER + nota.name
                                    conecta_ftp.storbinary('STOR ' + path_save, file_pdf)
                                    file_pdf = None #Limpa o conteudo da variavel
                                    print(f'O arquivo: {nota} foi salvo')
                                    query = "INSERT INTO python_notas_multilaser (file_name, upload_date, email_date, zip_file) VALUES ('" + nota.name + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', '" + email_client.date.strftime("%Y-%m-%d %H:%M:%S") + "', '"+ anexo.filename +"');" 
                                    cursor.execute(query)
                                    mydb.commit()
                                
                            else:
                                print(f' A nota {nota} já foi baixada')
                                continue

                else:
                    continue
                
    conecta_ftp.quit()
    mydb.close()



def read_email_madesa():
    print('---------------- Baixando notas dos e-mails da Madesa ----------------')

     #conexão com o banco de dados
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE
            )
    cursor = mydb.cursor()

    conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA,config.USERNAME_CONECTA,config.PASSWORD_CONECTA)
    
    today = date.today()
    past_days = date.today() - timedelta(3)

    email_client = MailBox(config.email_imap).login(config.email_user, config.email_password)
    list_emails = email_client.fetch(AND(from_= config.email_from_madesa, date_gte= past_days, date_lt=today), reverse=True)

    list_db = check_database.check_db_madesa(mydb= mydb, cursor= cursor)

    for email_client in list_emails:
        if len(email_client.attachments) > 0:
            for anexo in email_client.attachments:

                try:
                   if anexo.filename.endswith('.pdf'):
                        if anexo.filename in list_db:
                            print(f'O arquivo {anexo.filename} ja foi baixado')
                            continue
                        else:
                            if confirm_pdf_nota(anexo.filename):
                                print(f'Enviando o arquivo {anexo.filename}')
                                file_renamed = read_pdf.file_name_madesa(BytesIO(anexo.payload))

                                path_save = config.PATH_DANF_MADESA + file_renamed
                                conecta_ftp.storbinary('STOR ' + path_save, BytesIO(anexo.payload))
                                print(f'O arquivo: {file_renamed} foi salvo')
                                
                                query = "INSERT INTO python_notas_madesa (file_name, file_renamed, upload_date, email_date) VALUES ('" + anexo.filename + "', '" + file_renamed + "','" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', '" + email_client.date.strftime("%Y-%m-%d %H:%M:%S") + "');" 
                                cursor.execute(query)
                                mydb.commit()
                except Exception as e:
                    print(e)
                        
    conecta_ftp.quit()
    mydb.close()

def read_email_mvx():
    print('---------------- Baixando notas dos e-mails da Mvx ----------------')

     #conexão com o banco de dados
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE
            )
    cursor = mydb.cursor()

    conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA,config.USERNAME_CONECTA,config.PASSWORD_CONECTA)
    
    today = date.today()
    past_days = date.today() - timedelta(30)

    email_client = MailBox(config.email_imap).login(config.email_user, config.email_password)
    list_emails = email_client.fetch(AND(from_= config.email_mvx, date_gte= past_days, date_lt=today), reverse=True)

    list_db = check_database.check_db_mvx(mydb= mydb, cursor= cursor)

    for email_client in list_emails:
        if len(email_client.attachments) > 0:
            for anexo in email_client.attachments:
                try:
                   if anexo.filename.endswith('.xlsx'):
                        with open(anexo.filename, "wb") as f:
                            f.write(anexo.payload)
                            df_url = pd.read_excel(anexo.filename, engine= "openpyxl")
                            coluna_link = [coluna for coluna in df_url.columns if df_url[coluna].apply(lambda x: isinstance(x, str) and x.endswith('/pdf')).any()]
                            df_link = df_url[coluna_link]
                            df_link = df_link.dropna()
                            df_link= df_link.drop_duplicates()

                            for _, row in df_link.iterrows():
                                link_pdf = row[0]
                                if link_pdf not in list_db:
                                    response = requests.get(link_pdf)
                                    file_name = link_pdf.split('/')[4] + '.pdf'

                                    if response.status_code == 200:
                                        pdf =  response.content
                                        file_pdf  = BytesIO(pdf)

                                        path_save = config.PATH_DANF_MVX + file_name
                                        conecta_ftp.storbinary('STOR ' + path_save, file_pdf)
                                        print(f'O arquivo: {file_name} foi salvo')
                                        
                                        query = "INSERT INTO python_notas_mvx (file_name, link_nf, chave_nf, email_date, upload_date) VALUES ('" + anexo.filename + "', '" + link_pdf + "', '" + file_name + "', '" + email_client.date.strftime("%Y-%m-%d %H:%M:%S") + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "');" 
                                        cursor.execute(query)
                                        mydb.commit()
                                else:
                                    continue
                except Exception as e:
                    print(e)
                        
    conecta_ftp.quit()
    mydb.close()


def read_email_engage():
    print('---------------- Baixando notas dos e-mails da Engage ----------------')

    #Abre Conexão com o banco.
    mydb = mysql.connector.connect(
        host = config.DATABASE_HOST,
        user = config.DATABASE_USERNAME,
        password = config.DATABASE_PASSWORD,
        database = config.DATABASE_DATABASE
    )
    cursor = mydb.cursor()

    conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA, config.USERNAME_CONECTA, config.PASSWORD_CONECTA)

    today = date.today() + timedelta(1)
    past_days = date.today() - timedelta(30)
    list_db = check_database.check_db_engage(mydb, cursor)

    email_client = MailBox(config.email_imap).login(config.email_user, config.email_password)
    for email in config.email_engage:
        list_emails = email_client.fetch(AND(from_= email, date_gte= past_days, date_lt=today), reverse=True)
        for email in list_emails:
            if len(email.attachments) > 0:
                for anexo in email.attachments:
                    if anexo.filename.startswith('NFD') or anexo.filename.startswith('NF') and anexo.filename.endswith('.pdf'):
                        file_name = read_pdf.file_name_enage(BytesIO(anexo.payload))
                        if file_name not in list_db and file_name != False:
                            save_path = config.PATH_DANF_ENGAGE + file_name
                            conecta_ftp.storbinary('STOR ' + save_path, BytesIO(anexo.payload))
                            print(f'O arquivo: {file_name} foi salvo')
                            query2 = "INSERT INTO python_notas_engage (email, file_name, email_date, upload_date) VALUES ('"+ anexo.filename +"', '"+ file_name +"', '"+ email.date.strftime("%Y-%m-%d %H:%M:%S") +"', '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"');" 
                            cursor.execute(query2)
                        else:
                            continue
    conecta_ftp.quit()
    mydb.close()




def execute_read_emails():
    read_email_multilaser()
    read_email_madesa()
    read_email_engage()
    read_email_mvx()
    read_email_kabum()