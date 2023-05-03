

from sqlalchemy import text
from flask import jsonify
import pandas as pd
import json

from . import engine
from .tag_termo import TagTermo

class CategoriaTag:
    def __init__(self, id_categoria=None):
        if id_categoria is not None:
            self.__id_categoria = id_categoria
            query = text("SELECT * FROM tags_categoria WHERE ID = :id")
            result = engine.execute(query, {"id": self.__id_categoria}).fetchone()
            self.__nome_categoria = result['nome_categoria']
            self.__cor = result['cor']
    
    def consultar_id_categoria(self):
        return self.__id_categoria
    
    def consultar_nome_categoria(self):
        return self.__nome_categoria
    
    def consultar_cor(self):
        return self.__cor
    
    def consultar_tags(self):
        query = text("SELECT * FROM tags_info WHERE ID_categoria = :id")
        result = engine.execute(query, {"id": self.__id_categoria}).fetchall()
        tags = []
        for tag in result:
            tag = TagTermo(tag['ID'])
            tags.append(tag)
        return tags
    
    def consultar_dict_tags(self):
        tag_detail_dict = {}
        for i in self.consultar_tags():
            id_tag = i.consultar_id_tag()
            tag_detail_dict[id_tag] = i.consultar_nome_tag()
        return tag_detail_dict
    
    def adicionar_categoria_tag(self, form):
        query = text("INSERT INTO tags_categoria (nome_categoria, cor) VALUES (:nome_nova_cat, :cor_cat)")
        result = engine.execute(query, {"nome_nova_cat": form.nome_nova_cat, "cor_cat": form.cor_cat})
        id_categoria = result.lastrowid
        return id_categoria
    
    # def editar_nome_categoria(self, novo_nome):
    #     query = text("UPDATE tags_categoria SET nome_categoria = :nome WHERE ID = :id")
    #     engine.execute(query, {"nome": novo_nome, "id": self.__id_categoria})
    
    # def editar_cor(self, nova_cor):
    #     query = text("UPDATE tags_categoria SET cor = :cor WHERE ID = :id")
    #     engine.execute(query, {"cor": nova_cor, "id": self.__id_categoria})
    
    # def remover_tag(self, id_tag):
    #     query = text("DELETE FROM tags_info WHERE ID = :id")
    #     engine.execute(query, {"id": id_tag})