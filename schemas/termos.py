from typing import Dict, List
from datetime import date
from pydantic import BaseModel

from schemas import InfoTag

class StatusTermos(BaseModel):
    """ Retorna a quantidade de termos de compromisso que já foram classificados e que ainda estão pendentes de classificação."""
    classificados: int
    pendentes: int


class Termo(BaseModel):
    """ Retorna as informações sobre um termo de compromisso."""
    id: int
    numero_processo: str
    data_aprovacao: date
    data_assinatura: date
    data_publicacao: date
    compromitentes: str
    link_decisao: str
    data_arquivamento: date
    classificado: int
    link_parecer: str
    resumo: str
    tags: List[Dict[int, InfoTag]]


class Termos(BaseModel):
    """ Retorna uma lista de termos de compromisso."""
    termos: List[Termo]


class NewTermoSchema(BaseModel):
    """ Define como um novo termo de compromisso a ser inserido deve ser representado"""
    num_processo: str = "19957.002627/2022-48"
    data_aprovacao: date = '2023-05-08'
    data_assinatura: date = "2023-01-26"
    data_publicacao: date = "2023-03-06"
    compromitentes: str = "Charmant Empreendimento - Sociedade de Propósito Específico (SPE) Ltda. e Osvaldo Ottan Soares de Souza"
    URL_decisao: str = "https://conteudo.cvm.gov.br/decisoes/2023/20230131_R1/20230131_D2792.html"
    data_arquivamento: date = "2023-03-15"
    URL_parecer: str = "https://conteudo.cvm.gov.br/export/sites/cvm/decisoes/anexos/2023/20230131/2792_23.pdf"
    resumo: str = None


class IDTermoSchema(BaseModel):
    """ Retorna o id do termo de compromisso que foi inserido na base de dados."""
    id: int


class InputIDTermoSchema(BaseModel):
    """ Define como o id de um termo de compromisso deve ser representado."""
    id_termo: int 


class TagDeleteTermo(BaseModel):
    """ Define como um termo a ser deletada deve ser representada."""
    id_termo: int


class EditarTermoSchema(BaseModel):
    id_termo: int 
    num_processo: str = None
    data_aprovacao: date = None
    data_assinatura: date = None
    data_publicacao: date = None
    compromitentes: str = None
    URL_decisao: str = None
    data_arquivamento: date = None
    URL_parecer: str = None
    resumo: str = None