import requests
import base64
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
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_CARREFOR + file_name  #URl para baixar os PDFs
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
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_VIAVAREJO + file_name  #URl para baixar os PDFs
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


def send_pdf_kabum():
    print('---------------- Enviando Notas da Kabum ----------------')

    # SELECT para lista os nomes dos arquivos
    query = "SELECT file_name FROM python_notas_kabum WHERE ESL_Status IS NULL;"
    result = conexao_banco(query)

    #URL para acessar a API da ESL
    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # dos arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]  #Nome do arquivo na lista
        new_file_name = file_name.split('.')[0]  #Formata o nome do arquivo para ter apenas a chave NFe
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_KABUM + file_name  #URl para baixar os PDFs
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
                query2 = "UPDATE python_notas_kabum SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_name = '" + file_name + "';" 
                conexao_banco(query2)
                print(f"PDF em base64 enviado. Nota: {new_file_name}")
            else:
                print(f'Falha ao enviar o PDF. Código: {request.status_code}')


def send_pdf_multilaser():
    print('---------------- Enviando Notas da Multilaser ----------------')

    # SELECT para lista os nomes dos arquivos
    query = "SELECT file_name FROM python_notas_multilaser WHERE ESL_Status IS NULL;"
    result = conexao_banco(query)

    #URL para acessar a API da ESL
    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # dos arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]  #Nome do arquivo na lista
        new_file_name = file_name.split('.')[0]  #Formata o nome do arquivo para ter apenas a chave NFe
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_MULTILASER + file_name  #URl para baixar os PDFs
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
                query2 = "UPDATE python_notas_multilaser SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_name = '" + file_name + "';" 
                conexao_banco(query2)
                print(f"PDF em base64 enviado. Nota: {new_file_name}")
            else:
                print(f'Falha ao enviar o PDF. Código: {request.status_code}')




def send_pdf_madesa():
    print('---------------- Enviando Notas da Madesa ----------------')

    # SELECT para lista os nomes dos arquivos
    query = "SELECT file_renamed FROM python_notas_madesa WHERE ESL_Status IS NULL;" 
    result = conexao_banco(query)

    #URL para acessar a API da ESL
    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # dos arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]  #Nome do arquivo na lista
        new_file_name = file_name.split('.')[0]  #Formata o nome do arquivo para ter apenas a chave NFe
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_MADESA + file_name  #URl para baixar os PDFs
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
            query2 = "UPDATE python_notas_madesa SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_renamed = '" + file_name + "';" 
            conexao_banco(query2)


def send_pdf_madeira():
    print('---------------- Enviando Notas da Madeira  ----------------')

    query = "SELECT chave_notas FROM python_notas_madeira WHERE ESL_Status IS NULL;" 
    result = conexao_banco(query)

    #URL para acessar a API da ESL
    url_api = config.URL_BASE_API + config.URL_DANF_API

    #for para percorrer a lista com os nomes 
    # dos arquivos e enviar o PDF para a API
    for file_name in result:
        file_name = file_name[0]
        new_file_name = file_name.split('.')[0]
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_MADEIRA + file_name  #URl para baixar os PDFs
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
            query2 = "UPDATE python_notas_madeira SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE chave_notas = '" + file_name + "';" 
            conexao_banco(query2)

def send_pdf_engage():
    print('---------------- Enviando Notas da Engage  ----------------')

    query = "SELECT file_name FROM python_notas_engage WHERE ESL_Status IS NULL;"
    list_file = conexao_banco(query)

    url_api = config.URL_BASE_API + config.URL_DANF_API

    for file_name in list_file:
        file_name = file_name[0]
        name_api = file_name.split('.')[0]
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_ENGAGE + file_name
        base64 = pdf_to_base64(url_pdf)

        if base64:
            body = {
                "key": name_api,
                "pdf_string": base64  
                    }
            headers = {
                "Authorization": "Bearer "+config.TOKEN_UPLOAD+""
                }
            result = requests.post(url_api, json= body, headers= headers)
            if result.status_code == 200:
                print(f"PDF em base64 enviado. Nota: {name_api}")
                query2 = "UPDATE python_notas_engage SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_name = '" + file_name + "';"
                conexao_banco(query2)
            else:
                print(f'Falha ao enviar o PDF. Código: {result.status_code}')
    

def send_pdf_gazin():
    print('---------------- Enviando Notas da Gazin  ----------------')


    query = "SELECT file_name FROM python_notas_gazin WHERE ESL_Status IS NULL;"
    file_list = conexao_banco(query)

    url_api = config.URL_BASE_API + config.URL_DANF_API

    for file_name in file_list:
        file_name = file_name[0]
        name_api = file_name.split('.')[0]
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_GAZIN + file_name
        base64 = pdf_to_base64(url_pdf)

        if base64:
            body = {
                "key": name_api,
                "pdf_string": base64  
                    }
            headers = {
                "Authorization": "Bearer "+config.TOKEN_UPLOAD+""
                }
            result = requests.post(url_api, json= body, headers= headers)
            if result.status_code == 200:
                print(f"PDF em base64 enviado. Nota: {name_api}")
                query2 = "UPDATE python_notas_gazin SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_name = '" + file_name + "';"
                conexao_banco(query2)
            else:
                print(f'Falha ao enviar o PDF. Código: {result.status_code}')


def send_pdf_mvx():
    print('---------------- Enviando Notas da MVX  ----------------')
    
    query = "SELECT chave_nf FROM python_notas_mvx WHERE ESL_Status IS NULL"
    list_files = conexao_banco(query)
    url_api = config.URL_BASE_API + config.URL_DANF_API

    for file in list_files:
        file = file[0]
        file_api = file.split('.')[0]
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_MVX + file
        base64 = pdf_to_base64(url_pdf)
        
        if base64:
            body = {
                "key": file_api,
                "pdf_string": base64  
                    }
            headers = {
                "Authorization": "Bearer "+config.TOKEN_UPLOAD+""
                }
            result = requests.post(url_api, json= body, headers= headers)
            if result.status_code == 200:
                print(f"PDF em base64 enviado. Nota: {file}")
                query2 = "UPDATE python_notas_mvx SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE chave_nf = '" + file + "';"
                conexao_banco(query2)
            else:
                print(f'Falha ao enviar o PDF. Código: {result.status_code}')


def send_pdf_magazine():
    print('---------------- Enviando Notas da MAGAZINE  ----------------')
    
    query = "SELECT file_name FROM python_notas_magazine WHERE ESL_Status IS NULL"
    list_files = conexao_banco(query)
    url_api = config.URL_BASE_API + config.URL_DANF_API

    for file in list_files:
        file = file[0]
        file_api = file.split('.')[0]
        url_pdf = config.URL_CONECTA_PDF + config.URL_PDF_MAGAZINE + file + '.pdf'
        base64 = pdf_to_base64(url_pdf)
        
        if base64:
            body = {
                "key": file_api,
                "pdf_string": base64  
                    }
            headers = {
                "Authorization": "Bearer "+config.TOKEN_UPLOAD+""
                }

            result = requests.post(url_api, json= body, headers= headers)
            if result.status_code == 200:
                print(f"PDF em base64 enviado. Nota: {file}")
                query2 = "UPDATE python_notas_magazine SET ESL_Status = '"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "' WHERE file_name = '" + file + "';"
                conexao_banco(query2)
            else:
                print(f'Falha ao enviar o PDF. Código: {result.status_code}')

def execute_padf_to_64():
    send_pdf_carrefour()
    send_pdf_kabum()
    send_pdf_multilaser()
    send_pdf_viavarejo()
    send_pdf_madesa()
    send_pdf_madeira()
    send_pdf_engage()
    send_pdf_gazin()
    send_pdf_mvx()
send_pdf_magazine()