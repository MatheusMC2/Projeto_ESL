import io
import os
import config
import ftplib
import pandas as pd
import time 
import mysql.connector
from zipfile2 import ZipFile
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def get_chave_notas():
    today = date.today().strftime('%d-%m-%Y')
    yesterday = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    file_bytes = io.BytesIO()
    ocorrencias = ['/310/','/143/','/308/','/302/','/444/', '/222/', '/555/','/113/','/114/', '/312/', '/303/' , '/301/']

    inectar_ftp = ftplib.FTP(config.HOSTNAME_INECTAR, config.USERNAME_INECTAR, config.PASSWORD_INECTAR)
    inectar_ftp.cwd(config.PATH_TRIMESTRAL)
    list_files = inectar_ftp.nlst()

    for file in list_files:
        if not today in file: continue
        inectar_ftp.retrbinary('RETR ' + file, file_bytes.write)
        df = pd.read_excel(file_bytes)
    inectar_ftp.close()

    df['Data da ocorrência'] = pd.to_datetime(df['Data da ocorrência'])
    df = df.sort_values(by=['Data da ocorrência']).groupby(df['Chave NF-e']).last()
    df['Pagador do frete/Nome Fantasia'].fillna('', inplace=True)
    df= df[df["Pagador do frete/Nome Fantasia"].str.contains('MAGAZINE')]
    df.loc[:,"Código Ocorrência"] = '/'+df['Código Ocorrência'].astype(str)+'/'

    df_agendamento = df[df['Código Ocorrência'] == '/300/']
    df_agendamento.loc[:,'Observações'] = df_agendamento['Observações'].str.split().str[1]
    df_agendamento = df_agendamento[df_agendamento['Observações'] >= today]
    list_notas1 = df_agendamento['Chave NF-e'].to_list()

    df = df[df['Código Ocorrência'].isin(ocorrencias)]
    df = df[df['Data da ocorrência'] >= yesterday]
    list_notas2 = df['Chave NF-e'].to_list()

    list_notas = list_notas1 + list_notas2

    return list_notas


#conexão com o banco de dados
mydb = mysql.connector.connect(
    host = config.DATABASE_HOST,
    user = config.DATABASE_USERNAME,
    password = config.DATABASE_PASSWORD,
    database = config.DATABASE_DATABASE
)

list_db = []
cursor = mydb.cursor()
query = 'SELECT file_name FROM python_notas_magazine'
cursor.execute(query)
result = cursor.fetchall()

for name in result:
    list_db.append(name[0])

count = 0

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 50)

driver.maximize_window()
driver.get('https://lite.arquivei.com.br/batch')

login = driver.find_element(By.XPATH, '//*[@id="email"]')
login.send_keys('daniel@conectacargo.com.br')

password = driver.find_element(By.XPATH, '//*[@id="password"]')
password.send_keys('eP&$\\2<MD@')

iframe = driver.find_element(By.XPATH, '//*[@id="google-recaptcha"]/div/div/iframe')
driver.switch_to.frame(iframe)

recaptcha = driver.find_element(By.XPATH, '//*[@id="recaptcha-anchor"]/div[1]')
recaptcha.click()

driver.switch_to.default_content()

login_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="arquivei-sign-in"]/div[2]/form/div[4]/button[2]')))
login_botton.click()

list_notas = get_chave_notas()

for nota in list_notas:
    new_name =  nota + '.pdf'
    if nota in list_db or new_name in list_db:
        print(f'{nota} já foi baixada')
        continue
    search_nota = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="batch-access-key-input"]/textarea')))
    search_nota.send_keys(nota)
    search_nota.send_keys('\n')
    count += 1

    if count == 300:
        download_button = driver.find_element(By.XPATH, '//*[@id="batch-send"]/button')
        download_button.click()

        consulta_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="arquivei-hidden"]/div[2]/div/button[2]')))
        consulta_botton.click()

        lote_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="arquivei-hidden"]/div[2]/div/button[2]')))
        lote_botton.click()

        time.sleep(180)
        driver.refresh()

        meus_lotes_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tab-batch-reports"]')))
        meus_lotes_botton.click()

        download_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="batch-table"]/table/tbody/tr[1]/td[4]/button')))
        download_botton.click()

        pesquisa_botton = driver.find_element(By.XPATH, '//*[@id="tab-batch-generator"]')
        pesquisa_botton.click()
        count = 0

download_button = driver.find_element(By.XPATH, '//*[@id="batch-send"]/button')
download_button.click()

consulta_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="arquivei-hidden"]/div[2]/div/button[2]')))
consulta_botton.click()

lote_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="arquivei-hidden"]/div[2]/div/button[2]')))
lote_botton.click()

time.sleep(180)
driver.refresh()

meus_lotes_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tab-batch-reports"]')))
meus_lotes_botton.click()

download_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="batch-table"]/table/tbody/tr[1]/td[4]/button')))
download_botton.click()

pesquisa_botton = driver.find_element(By.XPATH, '//*[@id="tab-batch-generator"]')
pesquisa_botton.click()

time.sleep(10)
driver.quit()

inectar_ftp = ftplib.FTP(config.HOSTNAME_INECTAR, config.USERNAME_INECTAR, config.PASSWORD_INECTAR)

list_downloads = os.listdir('C:/Users/Matheus Monte/Downloads/')
zip_files = [zip for zip in list_downloads if zip.endswith('.zip') and zip.startswith('Arquivei')]

for zip in zip_files:
    print(zip)
    path = os.path.join('C:/Users/Matheus Monte/Downloads/', zip)
    with ZipFile(path, 'r') as file_zip:
        for file_info in file_zip.infolist():
            if file_info.filename.startswith('PDFs') and file_info.filename.lower().endswith('.pdf'):
                with file_zip.open(file_info.filename) as pdf:
                    pdf_content = pdf.read()
                    pdf_filename = os.path.basename(file_info.filename)
                    with open(pdf_filename, 'wb') as local_file:
                        local_file.write(pdf_content)
                    with open(pdf_filename, 'rb') as local_file:
                        inectar_ftp.storbinary('STOR /rpa/arquivos/nf_pdf/magazine/'+ pdf_filename, local_file)
                        query2 = "INSERT INTO python_notas_magazine (file_name) VALUES ('" + pdf_filename + "')"
                        cursor.execute(query2)
                        os.remove(pdf_filename)
    os.remove(path)
inectar_ftp.quit()