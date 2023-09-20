from read_email import execute_read_emails
from pdf_to_64 import execute_padf_to_64


print('Iniciando leitura dos e-mails')
execute_read_emails()
print('Enviando Notas para a API')
execute_padf_to_64()


