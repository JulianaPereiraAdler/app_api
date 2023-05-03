from pydantic import BaseModel
from typing import Dict, List


class RespostaChatGPTSchema(BaseModel):
    """ Retorna o resumo do parecer do termo de compromisso da CVM elaborado pelo ChatGPT"""
    resumo: str

class ResumoChatGPTSchema(BaseModel):
    """ Define os parâmetros para rodar a função que resume o texto do url passado utilizando o ChatGPT."""
    id_termo: int
    url: str
    key: str  = None
