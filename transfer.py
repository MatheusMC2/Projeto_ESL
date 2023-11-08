import os
import ftplib
import config

clientes = ['Carrefour', 'ViaVarejo', 'Kabum', 'Multilaser', 'Madesa', 'Mvx', 'MadeiraMadeira', 'Engage', 'Gazin']
conecta_ftp = ftplib.FTP(config.HOSTNAME_CONECTA, config.USERNAME_CONECTA, config.PASSWORD_CONECTA)

for cliente in clientes:
    folder  = '/public_html/CLIENTES/{}/EDI/NFPDF_PY/'.format(cliente)
    local_folder = '/home/devinectar.com.br/rpa/arquivos/nf_pdf/{}/'.format(cliente.lower())
    conecta_ftp.cwd(folder)
    list_files = conecta_ftp.nlst()
    for file in list_files:
        with open(f'{local_folder}/{file}', 'wb') as local_file:
            conecta_ftp.retrbinary('RETR ' + folder + file, local_file.write)