import requests
import base64
import config
import mysql.connector
from datetime import datetime

def conexao_banco_carrefour(x):
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE2
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


def send_pdf_carrefour():
    print('---------------- Enviando Notas da Carrefour ----------------')

    # SELECT para lista os nomes dos arquivos
    query = "SELECT Filename FROM python_carrefour_auto WHERE Renamed IS NULL AND FileType = 'NFPDF';" 
    result = conexao_banco_carrefour(query)

    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # do arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]  #Nome do arquivo na lista
        new_file_name = file_name.split('-')[1][3:]  #Formata o nome do arquivo para ter apenas a chave NFe
        url_pdf = f'https://inectar.com.br/CLIENTES/Carrefour/EDI/NFPDF_PY/{file_name}' #URl para baixar os PDFs
        base64_pdf = pdf_to_base64(url_pdf)

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
                query2 = "UPDATE python_carrefour_auto SET Renamed_Data = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', Renamed = '"+ new_file_name +"'  WHERE Filename = '" + file_name + "';" 
                conexao_banco_carrefour(query2)
            else:
                print(f'Falha ao enviar o PDF. Código: {request.status_code}')


def send_pdf_viavarejo():
    print('---------------- Enviando Notas da Via Varejo ----------------')
    #conexão com o banco de dados
    mydb = mysql.connector.connect(
            host = config.DATABASE_HOST,
            user = config.DATABASE_USERNAME,
            password = config.DATABASE_PASSWORD,
            database = config.DATABASE_DATABASE2
            )
    cursor = mydb.cursor()

    # SELECT para lista os nomes dos arquivos
    query = "SELECT Filename FROM python_viavarejo_auto WHERE Renamed IS NULL AND FileType = 'NFPDF';"
    cursor.execute(query)
    result = cursor.fetchall()

    #URL para acessar a API da ESL
    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # do arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]  #Nome do arquivo na lista
        new_file_name = file_name.split('_')[1]  #Formata o nome do arquivo para ter apenas a chave NFe
        url_pdf = f'https://inectar/public_html/CLIENTES/ViaVarejo/EDI/NFPDF_PY/{file_name}'  #URl para baixar os PDFs
        base64_pdf = pdf_to_base64(url_pdf)

        try:
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
                else:
                    print(f'Falha ao enviar o PDF. Código: {request.status_code}')
        except Exception as e:
            print(e)
        finally:
            #Atualizando coluna Rename no Banco de dados
            query2 = "UPDATE python_viavarejo_auto SET Renamed_Data = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "', Renamed = '"+ new_file_name +"'  WHERE Filename = '" + file_name + "';" 
            cursor.execute(query2)
            mydb.commit()
    mydb.close()

def execute_carrefour_via():
    send_pdf_viavarejo()
    send_pdf_carrefour()