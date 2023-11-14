import os
import requests
import base64
import PyPDF2
import config
import mysql.connector
from datetime import datetime

def conexao_banco(x):
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
        mydb.close()
        return result
    else:
        cursor.execute(x)
        mydb.commit()
        mydb.close()
        return


#função para converter o PDF em Base64
def pdf_to_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        pdf_content = response.content
        base64_content = base64.b64encode(pdf_content).decode('utf-8')
        return base64_content
    else:
        print(f"Failed to fetch PDF from URL. Status code: {response.status_code}")
        return None

def execute_padf_to_64():
    clientes = ['engage', 'gazin', 'kabum', 'madeiramadeira', 'madesa', 'magazine', 'multilaser', 'mvx']

    for cliente in clientes:
        print(f'---------------- Enviando Notas da {cliente} ----------------')

        # SELECT para lista os nomes dos arquivos
        query = f"SELECT file_name FROM python_notas_{cliente} WHERE ESL_Status IS NULL" 
        result = conexao_banco(query)

        url_api = config.URL_BASE_API + config.URL_DANF_API

        #for para percorrer a lista com os nomes 
        # do arquivos e enviar o PDF para a API
        for file_name in result:
            if not file_name in result: continue  #Nome do arquivo na lista
            elif '-' in file_name: new_file_name = file_name.split('-')[1][3:]  #Formata o nome do arquivo para ter apenas a chave NFe
            elif '.pdf' in file_name: new_file_name = file_name.replace('.pdf', '')
            elif 'NFe' in file_name: new_file_name = file_name.split('_')[1]
            else: new_file_name = file_name[0].replace('.pdf', '')

            url = f'https://rpa.devinectar.com.br/arquivos/nf_pdf/{cliente}/{file_name[0]}'

            base64_pdf = pdf_to_base64(url)

            #Envia a Base64 do PDF para API
            if base64_pdf:
                body = {
                        "key": new_file_name,
                        "pdf_string": base64_pdf
                        }
                headers = {
                "Authorization": "Bearer "+config.TOKEN_UPLOAD+""
                }
                request = requests.post(url_api, json= body, headers= headers)
                if request.status_code == 200:
                    print(f"PDF em base64 enviado. Nota: {new_file_name}")
                    query2 = f"UPDATE python_notas_{cliente} SET ESL_Status = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' WHERE file_name = '{file_name[0]}';" 
                    conexao_banco(query2)
                else:
                    print(f'Falha ao enviar o PDF. Código: {request.status_code}')

execute_padf_to_64()