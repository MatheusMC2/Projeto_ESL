import time
import config
import ftplib
import requests
import check_database
import read_pdf
import mysql.connector
from io import BytesIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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

def append_list(links_download, list_links):
    for cell in links_download:
        link = cell.get_attribute('href')
        list_links.append(link)


def get_list_links():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service= service)
    wait = WebDriverWait(driver, 30)
    contador = 0
    list_links = []

    driver.get('https://eagle.madeiramadeira.com.br/login') 

    email_input = driver.find_element('xpath', '//*[@id="eagle_login_container"]/div[1]/input')
    password_input = driver.find_element('xpath', '//*[@id="eagle_login_container"]/div[2]/input')

    email_input.send_keys('atendimento.madeira@conectacargo.com.br')
    password_input.send_keys('conecta123')

    login_botton = driver.find_element('xpath', '//*[@id="login_button"]')
    login_botton.click()

    menu_botton = wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="system_menu"]/ul[1]/li[1]/a')))
    menu_botton.click()

    coleta_reversa_botton = wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="system_menu"]/ul[1]/li[1]/ul/li[3]/a')))
    coleta_reversa_botton.click()

    filtrar_botton = driver.find_element(By.XPATH, '//*[@id="collect_schedule_datatable"]/thead/tr[1]/th[9]/button')
    filtrar_botton.click()

    registros_botton = wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="collect_schedule_datatable"]/thead/tr[1]/th[9]/ul/li[7]/label/span')))
    registros_botton.click()

    time.sleep(10)

    exibir_botton = wait.until(EC.element_to_be_clickable(('xpath', '//*[@id="collect_schedule_datatable_length"]/label/div/button')))
    actions = ActionChains(driver)
    actions.move_to_element(exibir_botton).perform()
    exibir_botton.click()

    exibir_100_botton = driver.find_element('xpath', '//*[@id="collect_schedule_datatable_length"]/label/div/div/ul/li[4]/a')
    exibir_100_botton.click()

    time.sleep(10)

    while True:
        links_download = driver.find_elements(By.XPATH, '//td[a[contains(@href, "/download-nota-devolucao")]]/a')
        append_list(links_download, list_links)

        try:
            next_botton = driver.find_element('xpath', '//*[@id="collect_schedule_datatable_next"]/a')
            next_botton.click()
            time.sleep(15)
        except Exception as e:
            print(e)
        if contador == 15:
            break
        else:
            contador += 1
    driver.quit()
    return list_links



print('---------------- Baixando notas dos e-mails da MadeiraMadeira ----------------')

conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA,config.USERNAME_CONECTA,config.PASSWORD_CONECTA)

count = 0
list_db = check_database.check_db_madeira()
list_links = get_list_links()

for link in list_links:
    response = requests.get(link)
    if response.status_code == 200:
        file_name = read_pdf.file_name_madeira(BytesIO(response.content))
        if file_name not in list_db and file_name != False:
            file_pdf = BytesIO(response.content)

            path_save = config.PATH_TO_MADEIRA + file_name
            conecta_ftp.storbinary('STOR ' + path_save, file_pdf)
            print(f'O arquivo {file_name} foi salvo.')

            query = "INSERT INTO python_notas_madeira (chave_notas, upload_date) VALUES ('" + file_name + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "');" 
            conexao_banco(query)
        else:
            count += 1
            continue
conecta_ftp.quit()

print(f'{count} notas já foram baixadas antes')