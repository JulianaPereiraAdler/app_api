from typing import Dict
from pydantic import BaseModel


class InfoTag(BaseModel):
    cor: str
    nome_categoria: str
    nome_tag: str


class TagCategoria(BaseModel):
    """ Define como uma categoria de tags será retornada: nome da categoria, cor dos tags dessa categoria e id + nomes do tags da categoria.
    """
    nome_categoria: str
    cor: str
    tags: Dict[int, str]


class TagCategoriaList(BaseModel):
    """ Define como a lista das categorias de tags será retornada.
    """
    __root__: Dict[int, TagCategoria]


class CadastraCategoriaTagSchema(BaseModel):
    """ Define como uma nova categoria de tag a ser cadastrada deve ser representada."""
    nome_nova_cat: str = "Nome da nova categoria"
    cor_cat: str = "#fc6016"


class IDCategoriaSchema(BaseModel):
    """ Retorna o id da categoria de tags que foi inserida na base de dados."""
    id: int


class CadastraTagSchema(BaseModel):
    """ Define como uma nova tag a ser cadastrada deve ser representada."""
    #id_categoria: int = 1
    id_categoria: int
    nome_tag: str = "Nome da nova tag"


class IDTagSchema(BaseModel):
    """ Retorna o id da categoria de tags que foi inserida na base de dados."""
    id: int


class InsereTagSchema(BaseModel):
    """ Define como a tag a ser associada a um termo de compromisso deve ser representada."""
    id_tag: int = 1
    id_termo: int = 1

    
class InfoTagRelacionamento(BaseModel):
    """ Retorna as informações sobre uma tag associada a um termo de compromisso (com o id do relacionamento)."""
    cor: str
    nome_categoria: str
    nome_tag: str
    id_relacionamento: int


class RelacionamentoTagTermoSchema(BaseModel):
    """ Define como a tag a ser associada a um termo de compromisso deve ser representada."""
    tag_dict: Dict[int, InfoTagRelacionamento]


class InfoTagTermoSchema(BaseModel):
    """ Define como a tag a ser associada a um termo de compromisso deve ser representada."""
    tag_dict: Dict[int, InfoTag]


class TagDeleteRequest(BaseModel):
    """ Define como a tag a ser deletada deve ser representada."""
    id_relacionamento: int

