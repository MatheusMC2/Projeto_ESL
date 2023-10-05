import PyPDF2
import re


def file_name_madesa(anexo):
    padrao = r'@\n(.*?)\nConsulta'
    pdf_reader = PyPDF2.PdfReader(anexo)

    pdf_text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_text += page.extract_text()

    file_name = re.findall(padrao, pdf_text)
    file = file_name[0]
    file = file.replace(' ','') + '.pdf'
    return file

def file_name_madeira(x):
    try:
        padrao = r'01/01\n(.*?)CHAVE'
        pdf_reader = PyPDF2.PdfReader(x)

        pdf_text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()

        file_name = re.findall(padrao, pdf_text)
        file = file_name[0]
        file = file.replace(' ','') + '.pdf'
        return file
    except IndexError:
       return False
    

def file_name_enage(x):
    try:
        padrao = r'ACESSO\n(.*?)DANFE'
        pdf_reader = PyPDF2.PdfReader(x)

        pdf_text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()

        file_name = re.findall(padrao, pdf_text)
        file = file_name[0]
        file = file.replace(' ','') + '.pdf'
        return file
    except IndexError:
       return False
    

def file_name_gazin(x):
    try:
        padrao = r'Autenticadora(.*?)DANFE'
        pdf_reader = PyPDF2.PdfReader(x)

        pdf_text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()
        file_name = re.findall(padrao, pdf_text)
        file = file_name[0]
        file = file.replace(' ','') + '.pdf'
        return file
    except IndexError:
       return False

def file_name_gazin2(x):
    try:
        padrao = r'Autenticadora(.*?)DANFE'
        pdf_reader = PyPDF2.PdfReader(x)

        pdf_text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()
        file_name = re.findall(padrao, pdf_text)
        file = file_name[0]
        file = file.replace(' ','') + '.pdf'
        return file
    except IndexError:
        try:
            padrao2 = r'ACESSO\n(.*?)\nConsulta'
            pdf_reader = PyPDF2.PdfReader(x)

            pdf_text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text()
            file_name = re.findall(padrao2, pdf_text)
            file = file_name[0]
            file = file.replace(' ','') + '.pdf'
            return file
        except IndexError:
            return False
            

def carta_correcao(x):
    try:
        padrao = r'\b\d{44}\b'
        pdf_reader = PyPDF2.PdfReader(x)
        pdf_text = ''
        for paga_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[paga_num]
            pdf_text += page.extract_text()
        if 'CC-e' in pdf_text:
            print('Carta de Correção')
            file_name = re.findall(padrao, pdf_text)
            file = file_name[0]
            return 'CC-e ' + file + '.pdf'
        else:
            return False
    except IndexError:
        try:
            padrao = r"\b\d{4}(?: \d{4}){10}\b"
            pdf_reader = PyPDF2.PdfReader(x)
            pdf_text = ''
            for paga_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[paga_num]
                pdf_text += page.extract_text()
            if 'CC-e' in pdf_text:
                print('Carta de Correção')
                file_name = re.findall(padrao, pdf_text)
                file = file_name[0]
                file = file_name.replace(' ','')
                return 'CC-e ' + file + '.pdf'
            else:
                return False
        except Exception as e:
            print(e)
            return False
