from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine
from .atividade import Atividade

class AtividadesRegistradas:
    def __init__(self):
        pass
    
    def define_atividade(self, id_atividade, user_name, descricao, timestamp, relacionamentos):
        self.__id_atividade = id_atividade
        self.__user_name = user_name
        self.__descricao = descricao
        self.__timestamp = timestamp
        self.__relacionamentos = relacionamentos
    
    def consultar_atividades(self, n_atividades=None, id_termo=None, id_atividade=None):
        query = """SELECT ID, user_name, descricao, timestamp, 
                            JSON_GROUP_OBJECT(id_termo, numero_processo) as termos_relacionados
                        FROM (
                            SELECT a.ID, a.user_name, a.descricao, a.timestamp, r.id_termo, t.numero_processo
                            FROM atividades as a
                            LEFT JOIN relacionamento_atividades_termos as r ON a.ID = r.id_atividade 
                            LEFT JOIN termos_compromisso as t ON r.id_termo = t.ID """
        if id_termo:
            query = query + """ WHERE t.ID =""" + str(id_termo)

        if id_atividade:
            query = query + """ WHERE a.ID =""" + str(id_atividade)

        query = query + """ ORDER BY a.timestamp DESC
                        ) as x
                        GROUP BY ID
                        ORDER BY timestamp DESC"""
        
        if n_atividades:
            query = query + """ LIMIT """ + str(n_atividades)
        
        result = engine.execute(text(query)).fetchall()
    
        lista_atividades = []
        for r in result:
            atividade = Atividade(r["ID"])
            lista_atividades.append(atividade)
        
        return lista_atividades
    
    def consultar_atividades_formatado(self, n_atividades=None, id_termo=None, id_atividade=None):
        lista_atividades = []
        for atividade in self.consultar_atividades(n_atividades, id_termo, id_atividade):
            dic_atividade = {'id_atividade': atividade.consultar_id_atividade(),
                            'user_name': atividade.consultar_user_name(),
                            'descricao': atividade.consultar_descricao(),
                            'timestamp': atividade.consultar_timestamp(),
                            'relacionamentos': atividade.consultar_json_relacionamentos()}
            lista_atividades.append(dic_atividade)
        return lista_atividades
    
    def adicionar_atividade(self, user_name, descricao, relacionamentos=None):
        query = text("""INSERT INTO atividades (user_name, descricao) 
                        VALUES (:user_name, :descricao)""")
        result = engine.execute(query, {"user_name": user_name, "descricao": descricao})
        id_atividade = result.lastrowid
        
        if relacionamentos is not None:
            for i in relacionamentos:
                query = text("""INSERT INTO relacionamento_atividades_termos (id_atividade, id_termo) 
                                VALUES (:id_atividade, :id_termo)""")
                result = engine.execute(query, {"id_atividade": id_atividade, "id_termo": i})
            
        return id_atividade
    
    def delete_atividade(self, id_atividade):
        query = text("""DELETE FROM atividades WHERE ID=:id_atividade""")
        engine.execute(query, {"id_atividade": id_atividade})
        return id_atividade