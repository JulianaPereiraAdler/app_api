from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine
from .tag_termo import TagTermo

class TermoCompromisso:
    def __init__(self, id_termo=None):
        if id_termo is not None:
            query = text("""SELECT t.*, d.* FROM termos_compromisso as t
                        LEFT JOIN termos_compromisso_detalhes as d ON d.ID_termo = t.ID
                        WHERE t.ID = :id""")
            result = engine.execute(query, {"id": id_termo}).fetchone()
            self.__id_termo = id_termo
            self.__numero_processo = result['numero_processo']
            self.__data_aprovacao = result['data_aprovacao']
            self.__data_assinatura = result['data_assinatura']
            self.__data_publicacao = result['data_publicacao']
            self.__compromitentes = result['compromitentes']
            self.__link_decisao = result['link_decisao']
            self.__data_arquivamento = result['data_arquivamento']
            self.__classificado = result['classificado']
            self.__link_parecer = result['link_parecer']
            self.__resumo = result['resumo']
        
    def consultar_id_termo(self):
        return self.__id_termo
    
    def consultar_numero_processo(self):
        return self.__numero_processo
    
    def consultar_data_aprovacao(self):
        return self.__data_aprovacao
    
    def consultar_data_assinatura(self):
        return self.__data_assinatura
    
    def consultar_data_publicacao(self):
        return self.__data_publicacao
    
    def consultar_compromitentes(self):
        return self.__compromitentes
    
    def consultar_link_decisao(self):
        return self.__link_decisao
    
    def consultar_data_arquivamento(self):
        return self.__data_arquivamento
    
    def consultar_classificado(self):
        return self.__classificado
    
    def consultar_link_parecer(self):
        return self.__link_parecer

    def consultar_resumo(self):
        return self.__resumo
      
    def consultar_tags(self):
        query = text("""SELECT ID, ID_tag FROM relacionamento_tags_termos WHERE ID_termo = :id""")
        result = engine.execute(query, {"id": self.__id_termo}).fetchall()
        dict_tags ={}
        for r in result:
            tag = TagTermo(r['ID_tag'])
            if r['ID'] not in dict_tags:
                dict_tags[r['ID']] = {}
            dict_tags[r['ID']] = tag.get_tag_info()
        return dict_tags

    def adicionar_novo_termo(self, form):
        query = text("""INSERT INTO termos_compromisso 
                    (numero_processo, data_aprovacao, data_assinatura, data_publicacao, compromitentes, link_decisao, data_arquivamento, classificado) 
                    VALUES (:numero_processo, :data_aprovacao, :data_assinatura, :data_publicacao, :compromitentes, :link_decisao, :data_arquivamento, 0)""")
        result = engine.execute(query, {"numero_processo": form.num_processo, "data_aprovacao": form.data_aprovacao, "data_assinatura": form.data_assinatura, "data_publicacao": form.data_publicacao, 
                            "compromitentes": form.compromitentes, "link_decisao": form.URL_decisao, "data_arquivamento": form.data_arquivamento})
        id_termo = result.lastrowid

        query = text("""INSERT INTO termos_compromisso_detalhes
                        (ID_termo, link_parecer, resumo) 
                        VALUES (:ID_termo, :link_parecer, :resumo)""")
        result = engine.execute(query, {"ID_termo": id_termo, "link_parecer": form.URL_parecer, "resumo":form.URL_parecer})
        id_termo_detalhe = result.lastrowid

        return id_termo
    
    def get_termo_formatado(self):
        dic_termo = {'id': self.consultar_id_termo(),
                    'numero_processo': self.consultar_numero_processo(),
                    'data_aprovacao': self.consultar_data_aprovacao(),
                    'data_assinatura': self.consultar_data_assinatura(),
                    'data_publicacao': self.consultar_data_publicacao(),
                    'compromitentes': self.consultar_compromitentes(),
                    'link_decisao': self.consultar_link_decisao(),
                    'data_arquivamento': self.consultar_data_arquivamento(),
                    'classificado': self.consultar_classificado(),
                    'link_parecer': self.consultar_link_parecer(),
                    'resumo': self.consultar_resumo(),
                    'tags': self.consultar_tags()}
        return dic_termo
    
    def delete_termo(self):
        query = text("""DELETE FROM termos_compromisso WHERE ID = :id_termo""")
        result= engine.execute(query, {"id_termo": self.__id_termo})
        return self.__id_termo
    
    def editar_termo(self, num_processo = None, data_aprovacao = None, data_assinatura = None, data_publicacao = None, compromitentes = None, URL_decisao = None, data_arquivamento = None, URL_parecer = None, resumo = None):
        query = "UPDATE termos_compromisso SET"
        params = {}

        if data_aprovacao is not None or data_assinatura is not None or data_publicacao is not None or compromitentes is not None or URL_decisao is not None or data_arquivamento is not None:
            if num_processo is not None:
                query += " numero_processo = :num_processo,"
                params["num_processo"] = num_processo

            if data_aprovacao is not None:
                query += " data_aprovacao = :data_aprovacao,"
                params["data_aprovacao"] = data_aprovacao

            if data_assinatura is not None:
                query += " data_assinatura = :data_assinatura,"
                params["data_assinatura"] = data_assinatura

            if data_publicacao is not None:
                query += " data_publicacao = :data_publicacao,"
                params["data_publicacao"] = data_publicacao

            if compromitentes is not None:
                query += " compromitentes = :compromitentes,"
                params["compromitentes"] = compromitentes

            if URL_decisao is not None:
                query += " link_decisao = :URL_decisao,"
                params["URL_decisao"] = URL_decisao

            if data_arquivamento is not None:
                query += " data_arquivamento = :data_arquivamento,"
                params["data_arquivamento"] = data_arquivamento

            query = query.rstrip(",") + " WHERE ID = :id_termo"
            params["id_termo"] = self.__id_termo
            result = engine.execute(text(query), params)

        if URL_parecer is not None:
            query_has_parecer = text("""SELECT link_parecer FROM termos_compromisso_detalhes WHERE ID_termo = :id_termo""")
            result_has_parecer = engine.execute(query_has_parecer, {"id_termo": self.__id_termo}).fetchone()

            if result_has_parecer:
                query_detalhes = text("""UPDATE termos_compromisso_detalhes SET link_parecer = :URL_parecer WHERE ID_termo = :id_termo""")
                result = engine.execute(query_detalhes, {"URL_parecer": URL_parecer, "id_termo": self.__id_termo})
            else: 
                query_detalhes = text("""INSERT INTO termos_compromisso_detalhes (ID_termo, link_parecer) VALUES (:id_termo, :URL_parecer)""")
                result = engine.execute(query_detalhes, {"URL_parecer": URL_parecer, "id_termo": self.__id_termo})
        
        if resumo is not None:
            query_has_resumo = text("""SELECT resumo FROM termos_compromisso_detalhes WHERE ID_termo = :id_termo""")
            result_has_resumo = engine.execute(query_has_resumo, {"id_termo": self.__id_termo}).fetchone()

            if result_has_resumo:
                query_detalhes = text("""UPDATE termos_compromisso_detalhes SET resumo = :resumo WHERE ID_termo = :id_termo""")
                result = engine.execute(query_detalhes, {"resumo": resumo, "id_termo": self.__id_termo})
            else: 
                query_detalhes = text("""INSERT INTO termos_compromisso_detalhes (ID_termo, resumo) VALUES (:id_termo, :resumo)""")
                result = engine.execute(query_detalhes, {"resumo": resumo, "id_termo": self.__id_termo})

        return self.__id_termo
    
    def update_status_termo(self):
        
        n_tags = len(self.consultar_tags())
        if n_tags == 0:
            query = text("""UPDATE termos_compromisso SET classificado = 0 WHERE ID = :id_termo""")
            result = engine.execute(query, {"id_termo": self.__id_termo})
        else:
            query = text("""UPDATE termos_compromisso SET classificado = 1 WHERE ID = :id_termo""")
            result = engine.execute(query, {"id_termo": self.__id_termo})

        return self.__id_termo

    def update_resumo_termo(self, texto_resumo):
        
        if self.consultar_resumo() != "":
            query_detalhes = text("""UPDATE termos_compromisso_detalhes SET resumo = :resumo WHERE ID_termo = :id_termo""")
            result = engine.execute(query_detalhes, {"resumo": texto_resumo, "id_termo": self.__id_termo})
        else: 
            query_detalhes = text("""INSERT INTO termos_compromisso_detalhes (ID_termo, resumo) VALUES (:id_termo, :resumo)""")
            result = engine.execute(query_detalhes, {"resumo": texto_resumo, "id_termo": self.__id_termo})

        return texto_resumo