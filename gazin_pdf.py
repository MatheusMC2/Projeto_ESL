import re
import time
import config
import ftplib
import requests
import read_pdf
from io import BytesIO
from datetime import datetime
from selenium import webdriver
from conexao_banco import conexao_banco
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

def download_pdf(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f'Falha ao Baixar o PDF: {url}. Erro: {response.status_code}')
            return None
    except Exception as e:
        print(f'Falha ao baixar o arquivo. {str(e)}')


def upload_to_ftp(file_content, path):
    try:
        conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA, config.USERNAME_CONECTA, config.PASSWORD_CONECTA)
        conecta_ftp.storbinary('STOR ' + path, BytesIO(file_content))
        conecta_ftp.quit()
        print(f'O arquivo {path} foi enviado para o servidor FTP.')
    except Exception as e:
        print(f'Erro ao enviar o arquivo para o servidor FTP: {str(e)}')

        
def get_links(driver):
    list_links = []
    wait = WebDriverWait(driver, 10)

    driver.get('https://admgazin.precode.com.br/SG/externo/transportadora/listaTransportadora.php')
    driver.maximize_window()


    id_login = driver.find_element(By.XPATH, '//*[@id="logs"]')
    id_login.send_keys('conectacargo')

    id_password = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div/form/div[2]/input')
    id_password.send_keys('Conecta@2023')

    login_botton = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div/form/input[4]')
    login_botton.click()
    time.sleep(5)

    bottons = driver.find_elements(By.XPATH, '//*[contains(@id, "linha")]/td[20]/center/a/div[1]')

    for botton in bottons:
        botton.click()
        driver.implicitly_wait(5)
        iframe = driver.find_element(By.XPATH, '//*[@id="myIframe"]')
        driver.switch_to.frame(iframe)
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            url = link.get_attribute('href')
            if url.endswith('.pdf') and 'Check' not in url and 'Ressalva' not in url:
                list_links.append(url)
            else:
                continue
        driver.switch_to.default_content()
        driver.find_element(By.XPATH, '//*[@id="popup"]/div/div/div[1]').click()

    search_botton = driver.find_element(By.XPATH, '//*[@id="telaprincipal"]/div[1]/div[3]/a')
    search_botton.click()

    driver.find_element(By.XPATH, '//*[@id="mostlojas"]/p/input').send_keys('GazinGO')
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="mostlojas"]/table/tbody/tr[40]/td[5]').click()

    id_login = driver.find_element(By.XPATH, '//*[@id="logs"]')
    id_login.send_keys('conectacargo')

    id_password = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div/form/div[2]/input')
    id_password.send_keys('Conecta@2023')

    login_botton = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div/form/input[4]')
    login_botton.click()


    bottons = driver.find_elements(By.XPATH, '//*[contains(@id, "linha")]/td[20]/center/a/div[1]')

    for botton in bottons:
        botton.click()
        driver.implicitly_wait(5)
        iframe = driver.find_element(By.XPATH, '//*[@id="myIframe"]')
        driver.switch_to.frame(iframe)
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            url = link.get_attribute('href')
            if url.endswith('.pdf') and 'Check' not in url and 'Ressalva' not in url:
                list_links.append(url)
            else:
                continue
        driver.switch_to.default_content()
        driver.find_element(By.XPATH, '//*[@id="popup"]/div/div/div[1]').click()
    

    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get('https://posvenda.gazinatacado.com.br/sac/tickets')

    id_login3 = driver.find_element(By.XPATH, '//*[@id="kt_login_signin_form"]/div[1]/input')
    id = '21568198825'

    for char in id:
        id_login3.send_keys(char)
        time.sleep(0.1)

    password_login = driver.find_element(By.XPATH, '//*[@id="kt_login_signin_form"]/div[2]/input')
    password_login.send_keys('conecta1234')

    login_botton3 = driver.find_element(By.XPATH, '//*[@id="kt_login_signin_submit"]')
    login_botton3.click()
    time.sleep(3)


    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    filter_botton2 = driver.find_element(By.XPATH, '//*[@id="tickets_table"]/div/div/div/button')
    filter_botton2.click()
    filter_botton2.click()
    filter_botton2.click()

    filter50 = driver.find_element(By.XPATH, '//*[@id="bs-select-1-4"]/span')
    filter50.click()

    limit_str = driver.find_element(By.XPATH, '//*[@id="tickets_table"]/div/div/span').text
    limit = re.sub(r'[a-zA-Z]', '', limit_str)
    limit = limit.split(' ')[3]
    limit = int(limit)

    driver.execute_script("window.scrollTo(0, 0);")
    bottons = driver.find_elements(By.XPATH, '//*[@id="tickets_table"]/table/tbody/tr/td[8]/span/a')

    for i in range(1, limit + 1):
        time.sleep(3)
        xpath = '//*[@id="tickets_table"]/table/tbody/tr[{}]/td[8]/span/a'.format(i)
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", element)
        nao_botton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kt_body"]/div[17]/div/div[3]/button[3]')))
        nao_botton.click()
        links = driver.find_elements(By.CSS_SELECTOR, 'a.download_attachment')
        for link in links:
            link = link.get_attribute('data-item')
            if 'pdf' in link:
                list_links.append(link)
        back_botton = driver.find_element(By.XPATH, '//*[@id="kt_content"]/div[2]/div/div/div/div[1]/div/div[1]/div[2]/a')
        back_botton.click()
        time.sleep(3)
    return list_links

print('---------------------- Baixando Notas da Gazin ----------------------')
query = "SELECT file_name FROM python_notas_gazin;"
list_db = conexao_banco(query)
conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA, config.USERNAME_CONECTA, config.PASSWORD_CONECTA)
count = 0

while True:
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        links = get_links(driver)
        driver.quit()
    except WebDriverException:
        print('Ocorreu um erro, reiniciando.')
        driver.quit()
    else:
        for link in links:
            if 'atacado' in link:
                result = download_pdf(link)
                if result:
                    file_name =  read_pdf.file_name_gazin2(BytesIO(result))
                    if file_name in list_db:
                        count += 1
                    elif file_name != False:
                        path_save = config.PATH_DANF_GAZIN + file_name
                        upload_to_ftp(result, path_save)
                        query2 = "INSERT INTO python_notas_gazin (file_name, upload_date) VALUES ('" + file_name + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "');"
                        conexao_banco(query2)
                        print(f'O arquivo {file_name} foi salvo no banco de dados.')
            else:
                result = download_pdf(link)
                if result:
                    file_name2 =  read_pdf.file_name_gazin(BytesIO(result))
                    if file_name2 in list_db:
                        count += 1
                    elif file_name2 != False:
                        path_save = config.PATH_DANF_GAZIN + file_name2
                        upload_to_ftp(result, path_save)
                        query2 = "INSERT INTO python_notas_gazin (file_name, upload_date) VALUES ('" + file_name2 + "', '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "');"
                        conexao_banco(query2)
                        print(f'O arquivo {file_name2} foi salvo.')

        print(f'Total de notas que já haviam sido baixadas: {count}')
        break
