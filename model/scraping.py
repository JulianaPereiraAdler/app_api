import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from sqlalchemy import text, create_engine
import json
from datetime import datetime

from . import engine

def function_scraping_cvm():

    url = 'https://conteudo.cvm.gov.br/system/modules/br.com.squadra.principal/elements/resultadoTermoCompromisso.jsp'

    n_pag = 1
    final = 0
    lista_todos_termos = []
    lista_erros = []

    mensagem = ""
    novos_termos_inseridos = []

    while final == 0:
        print("\nBuscando página:", n_pag)
        headers = {'user-agent':'Mozilla/4.0'}
        resposta = requests.get(url,
                                headers = headers, params = {'searchPage': n_pag, 'itensPagina':100})
        resposta = resposta.text

        r1 = BeautifulSoup(resposta, 'html.parser')

        lista_termos = r1.find_all('tr')

        if len(lista_termos) > 0:
            lista_termos.pop(0)
            print("Quantidade de resultados:", len(lista_termos))

            erro_parte_1 = 0
            
            for i in lista_termos:
                
                try: 
                    num_processo = i.contents[1].text
                    link_processo = i.contents[1].find("a").get("href")
                    if "conteudo.cvm.gov.br" not in link_processo:
                        link_processo = 'https://conteudo.cvm.gov.br' + link_processo
                        
                    data_aprovacao = i.contents[3].get_text(strip=True)
                    #data_aprovacao = datetime.strptime(data_aprovacao, '%d/%m/%Y').strftime('%Y-%m-%d')
                    
                    data_assinatura= i.contents[5].get_text(strip=True)
                    #data_assinatura = datetime.strptime(data_assinatura, '%d/%m/%Y').strftime('%Y-%m-%d')
                    
                    data_publicacao= i.contents[7].get_text(strip=True)
                    #data_publicacao = datetime.strptime(data_publicacao, '%d/%m/%Y').strftime('%Y-%m-%d')

                    compromitentes= i.contents[9].text
                    link_decisao = i.contents[11]
                    link_decisao = link_decisao.find("a").get("href")
                    
                    if "conteudo.cvm.gov.br" not in link_decisao:
                        link_decisao = 'https://conteudo.cvm.gov.br' + link_decisao

                    data_arquivamento = i.contents[13].get_text(strip=True)
                    #data_arquivamento = datetime.strptime(data_arquivamento, '%d/%m/%Y').strftime('%Y-%m-%d')

                    lista_todos_termos.append((num_processo,link_processo,data_aprovacao,data_assinatura,data_publicacao,compromitentes,link_decisao,data_arquivamento))       
            
                except:
                    if erro_parte_1 == 0:
                        mensagem = str(i.contents[1].text)
                    else:
                        mensagem = mensagem +", " + str(i.contents[1].text)
                    lista_erros.append(i.contents[1].text)
                    erro_parte_1 = erro_parte_1 + 1
            
            n_pag = n_pag + 1

        else:
            final = 1
            print('Final das páginas \n')
            
            
    df_termos = pd.DataFrame(lista_todos_termos,columns=['num_processo','link_processo', 'data_aprovacao', 'data_assinatura', 'data_publicacao', 'compromitentes', 'link_decisao', 'data_arquivamento'])
    df_termos['num_processo'].astype('str')
    df_termos['link_parecer'] = ''

    ######## APENAS PARA TESTE ########
    #-----------------------------------
    df_termos = df_termos.head(25)

    #monta lista com termos já cadastrados
    query = text("""SELECT numero_processo FROM termos_compromisso WHERE 1""")
    result = engine.execute(query).fetchall()
    lista_num_termos = []
    for r in result:
        if r['numero_processo'] not in lista_num_termos:
            lista_num_termos.append(r['numero_processo'])

    #df de termos que não estão no nosso banco
    filtered_df = df_termos[~df_termos["num_processo"].isin(lista_num_termos)]

    #formatar datas
    filtered_df['data_aprovacao'] = pd.to_datetime(filtered_df['data_aprovacao'], format='%d/%m/%Y')
    filtered_df['data_aprovacao'] = filtered_df['data_aprovacao'].dt.strftime('%Y-%m-%d')

    filtered_df['data_assinatura'] = pd.to_datetime(filtered_df['data_assinatura'], format='%d/%m/%Y')
    filtered_df['data_assinatura'] = filtered_df['data_assinatura'].dt.strftime('%Y-%m-%d')

    filtered_df['data_publicacao'] = pd.to_datetime(filtered_df['data_publicacao'], format='%d/%m/%Y')
    filtered_df['data_publicacao'] = filtered_df['data_publicacao'].dt.strftime('%Y-%m-%d')

    filtered_df['data_arquivamento'] = pd.to_datetime(filtered_df['data_arquivamento'], format='%d/%m/%Y')
    filtered_df['data_arquivamento'] = filtered_df['data_arquivamento'].dt.strftime('%Y-%m-%d')


    for index, row in filtered_df.iterrows():
        # get the link from the "link_decisao" column
        try:
            link_decisao = row['link_decisao']
            response = requests.get(link_decisao)
            soup = BeautifulSoup(response.content, 'html.parser')
            content_veja_mais = soup.find('div', {'class': 'boxVejaMais'})

            try: 
                parecer_link = content_veja_mais.find(lambda tag:tag.name=="a" and "PARECER" in tag.text).get("href")
                
                if "conteudo.cvm.gov.br" not in parecer_link:
                    parecer_link = 'https://conteudo.cvm.gov.br' + parecer_link
                filtered_df.at[index, 'link_parecer'] = parecer_link

            except:
                try: 
                    parecer_link = content_veja_mais.find(lambda tag:tag.name=="a" and "RELATOR" in tag.text).get("href")

                    if "conteudo.cvm.gov.br" not in parecer_link:
                        parecer_link = 'https://conteudo.cvm.gov.br' + parecer_link
                    filtered_df.at[index, 'link_parecer'] = parecer_link
                except:
                    print('Erro no processo:', row['link_decisao'], "- Não encontrou link parecer e nem link voto do relator")
        except:
            print('Erro no processo:', row['num_processo'], "- link_decisao:", row['link_decisao'])
            

    erro_mensagem_banco = ""
    i = 0 
    for i, row in filtered_df.iterrows():
        query = text("""INSERT INTO termos_compromisso (numero_processo, data_aprovacao, data_assinatura, data_publicacao, 
                        compromitentes, link_decisao, data_arquivamento) 
                        VALUES (:numero_processo, :data_aprovacao, :data_assinatura, :data_publicacao, :compromitentes, :link_decisao, :data_arquivamento)""")
        try:
            result = engine.execute(query, {"numero_processo":row['num_processo'],
                                            "data_aprovacao": row['data_aprovacao'],
                                            "data_assinatura": row['data_assinatura'],
                                            "data_publicacao": row['data_publicacao'],
                                            "compromitentes": row['compromitentes'],
                                            "link_decisao": row['link_decisao'],
                                            "data_arquivamento": row['data_arquivamento']})
            termo_id = result.lastrowid
            novos_termos_inseridos.append(termo_id)

            if row['link_decisao'] != "" or row['link_decisao'] != None:
                query = text("""INSERT INTO termos_compromisso_detalhes (ID_termo, link_parecer) VALUES (:ID_termo, :link_parecer)""")
                result = engine.execute(query, {"ID_termo":termo_id, "link_parecer": row['link_parecer']})    
        
        except:
            if i == 0:
                erro_mensagem_banco = row['num_processo']
            else:
                erro_mensagem_banco = erro_mensagem_banco + ", " +  row['num_processo']
                i +=1

    termos_inseridos = "Termos Inseridos com sucesso: " + str(len(novos_termos_inseridos)) 

    if mensagem != "":
        erro_mensagem_scraping_final = "Erro durante scraping do site da CVM: " + mensagem
    else:
        erro_mensagem_scraping_final = "Nenhum erro encontrado scraping do site da CVM."

    mensagem_final = termos_inseridos + " | " + erro_mensagem_scraping_final

    if erro_mensagem_banco != "":
        erro_mensagem_banco_final = "Erro ao inserir termos no banco de dados: " + erro_mensagem_banco
    else:
        erro_mensagem_banco_final = "Nenhum erro encontrado ao inserir termos no banco de dados."

    mensagem_final = mensagem_final + " | " + erro_mensagem_banco_final

    resposta = {}
    resposta['mensagem'] = mensagem_final
    resposta['termos_inseridos'] = novos_termos_inseridos
    
    return resposta
