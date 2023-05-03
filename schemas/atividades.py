from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date

from schemas import IDTermoSchema

class AtividadeSchema(BaseModel):
    id_atividade: int
    user_name: str
    descricao: str
    timestamp: date
    relacionamentos: Dict[int, str]


class AtividadesRegistradasSchema(BaseModel):
    lista_atividades: List[AtividadeSchema]


class InputAtividadesRegistradas(BaseModel):
    """Parâmetros opcionais para consulta de atividades registradas."""
    n_atividades: int = None
    id_termo: int = None


class InserirAtividadeSehema(BaseModel):
    """Define os parâmetros para inserir uma atividade no banco de dados."""
    user_name: str
    descricao: str
    relacionamentos: str = None


class TagDeleteAtividade(BaseModel):
    """ Define como a atividade a ser deletada deve ser representada."""
    id_atividade: int