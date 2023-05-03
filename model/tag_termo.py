
from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine

class TagTermo:
    def __init__(self, id_tag=None):
        if id_tag is not None:
            query = text("""SELECT i.nome_tag, c.ID as id_categoria, c.nome_categoria, c.cor FROM tags_info as i
                        INNER JOIN tags_categoria as c ON c.ID = i.ID_categoria
                        WHERE i.ID = :id""")
            result = engine.execute(query, {"id": id_tag}).fetchone()
            self.__id_tag = id_tag
            self.__nome_tag = result['nome_tag']
            self.__nome_categoria = result['nome_categoria']
            self.__id_categoria = result['id_categoria']
            self.__cor = result['cor']
        
    def consultar_id_tag(self):
        return self.__id_tag
    
    def consultar_nome_tag(self):
        return self.__nome_tag
    
    def consultar_nome_categoria(self):
        return self.__nome_categoria
    
    def consultar_cor(self):
        return self.__cor
    
    def get_tag_info(self):
        tag = {}
        if self.__id_tag not in tag:
            tag[self.__id_tag]={}
        tag[self.__id_tag]['nome_tag'] = self.__nome_tag
        tag[self.__id_tag]['nome_categoria'] = self.__nome_categoria
        tag[self.__id_tag]['cor'] = self.__cor
        tag[self.__id_tag]['id_categoria'] = self.__id_categoria
        return tag
        
    def cadastra_nova_tag(self, form):
        query = text("""INSERT INTO tags_info (nome_tag, ID_categoria) VALUES (:nome_tag, :id_categoria)""")
        result = engine.execute(query, {"nome_tag": form.nome_tag, "id_categoria": form.id_categoria})
        id_tag = result.lastrowid
        return id_tag
    
    def insere_novo_relacionamento_tag_termo(self, form):
        query = text("""INSERT INTO relacionamento_tags_termos (ID_tag, ID_termo) VALUES (:id_tag, :id_termo)""")
        result = engine.execute(query, {"id_tag": form.id_tag, "id_termo": form.id_termo})
        id_relacionamento = result.lastrowid
        return id_relacionamento
    
    def get_tag_info_por_id_relacionamento(self, id_relacionamento):
        query = text("""SELECT ID_tag FROM relacionamento_tags_termos WHERE ID = :id_relacionamento""")
        result = engine.execute(query, {"id_relacionamento": id_relacionamento}).fetchone()
        id_tag =  result['ID_tag']
        return  id_tag

    def get_tag_info_com_relacionamento(self, id_relacionamento):
        tag = {}
        if self.__id_tag not in tag:
            tag[self.__id_tag]={}
        tag[self.__id_tag]['nome_tag'] = self.__nome_tag
        tag[self.__id_tag]['nome_categoria'] = self.__nome_categoria
        tag[self.__id_tag]['cor'] = self.__cor
        tag[self.__id_tag]['id_relacionamento'] = id_relacionamento
        return tag

    def delete_relacionamento_tag_termo(self, id_relacionamento):
        query = text("""DELETE FROM relacionamento_tags_termos WHERE ID = :id_relacionamento""")
        engine.execute(query, {"id_relacionamento": id_relacionamento})
        return id_relacionamento