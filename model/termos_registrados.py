from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine

class TermosRegistrados:
    def __init__(self):
        self.__termos_registrados = []
        
    def registrar_termo(self, termo):
        self.__termos_registrados.append(termo)
    
    def get_status_termos(self):
        qnt_pendentes= 0
        qnt_classificado = 0
        for termo in self.__termos_registrados:
            if termo.consultar_classificado() == 0:
                qnt_pendentes = qnt_pendentes + 1
            else:
                qnt_classificado = qnt_classificado + 1
            
        resposta = {}
        resposta['classificados'] = qnt_classificado
        resposta['pendentes'] = qnt_pendentes
        return resposta
    
    def get_todos_termos_formatado(self):
        lista_termos = []
        for termo in self.__termos_registrados:
            dic_termo = {'id': termo.consultar_id_termo(),
                        'numero_processo': termo.consultar_numero_processo(),
                        'data_aprovacao': termo.consultar_data_aprovacao(),
                        'data_assinatura': termo.consultar_data_assinatura(),
                        'data_publicacao': termo.consultar_data_publicacao(),
                        'compromitentes': termo.consultar_compromitentes(),
                        'link_decisao': termo.consultar_link_decisao(),
                        'data_arquivamento': termo.consultar_data_arquivamento(),
                        'classificado': termo.consultar_classificado(),
                        'link_parecer': termo.consultar_link_parecer(),
                        'tags': termo.consultar_tags()}
            lista_termos.append(dic_termo)
        return lista_termos
    
    
    
    



                
