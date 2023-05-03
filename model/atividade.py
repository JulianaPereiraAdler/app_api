from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine
from .termo_compromisso import TermoCompromisso

class Atividade:
    def __init__(self, id_atividade):
        query = text("""SELECT ID, user_name, descricao, timestamp, 
                            JSON_GROUP_OBJECT(id_termo, numero_processo) as termos_relacionados
                        FROM (
                            SELECT a.ID, a.user_name, a.descricao, a.timestamp, r.id_termo, t.numero_processo
                            FROM atividades as a
                            LEFT JOIN relacionamento_atividades_termos as r ON a.ID = r.id_atividade 
                            LEFT JOIN termos_compromisso as t ON r.id_termo = t.ID
                            WHERE a.ID=:id_atividade
                            ORDER BY a.timestamp DESC
                        ) as x
                            GROUP BY ID
                            ORDER BY timestamp DESC""")
        result = engine.execute(query, {"id_atividade": id_atividade}).fetchone()
        self.__id_atividade = id_atividade
        self.__user_name = result['user_name']
        self.__descricao = result['descricao']
        self.__timestamp = result['timestamp']
        self.__relacionamentos = result['termos_relacionados']
        
    def consultar_id_atividade(self):
        return self.__id_atividade 
    
    def consultar_user_name(self):
        return self.__user_name
    
    def consultar_descricao(self):
        return self.__descricao
    
    def consultar_timestamp(self):
        return self.__timestamp
    
    def consultar_json_relacionamentos(self):
        return self.__relacionamentos
    
    def consultar_relacionamentos(self):
        """Retorna lista da termos relacionados a atividade"""
        relacionamentos = json.loads(self.__relacionamentos)
        relacionamentos_termo = []
        for i in relacionamentos:
            termo = TermoCompromisso(i)
            relacionamentos_termo.append(termo)
        return relacionamentos_termo       