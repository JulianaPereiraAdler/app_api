import PyPDF2
import textwrap
import openai
import requests
from io import BytesIO


def resume_chatgpt(key, texto_termo):
    openai.api_key = key

    #print("Aquii", texto_termo)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Hi!"},
            {"role": "user", "content": "Resume em português por favor: '\n\n" + texto_termo + "'"},
        ]
    )

    result = ""
    for choice in response.choices:
        result += choice.message.content
    return result


def consolidado_resumo_chatgpt(key, url):

    r = requests.get(url)
    print("URL", url)

    memoryFile = BytesIO(r.content)
    pdfreader = PyPDF2.PdfReader(memoryFile)
    
    #This will store the number of pages of this pdf file
    x = len(pdfreader.pages) 

    text = ""
    for page_num in range(len(pdfreader.pages)):
        page = pdfreader.pages[page_num]
        text += page.extract_text()

    lista_textos = textwrap.wrap(text, width=2000*4)

    texto_final = ""
    for t in lista_textos:
        resumo = resume_chatgpt(key, t)
        texto_final += resumo
    texto_final = resume_chatgpt(key, texto_final)

    return texto_final

