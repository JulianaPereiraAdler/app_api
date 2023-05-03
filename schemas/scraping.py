from pydantic import BaseModel
from typing import Dict, List

# class ScrapingCVMSchema(BaseModel):
#     """ Define os parâmetros para rodar o scraping que buscar o dados no site da CVM e inserir uma atividade no banco de dados."""
#     user_name: str

class RespostaScrapingCVMSchema(BaseModel):
    """ Define os parâmetros para rodar o scraping que buscar o dados no site da CVM e inserir uma atividade no banco de dados."""
    mensagem: str
    termos_inseridos: List[int]