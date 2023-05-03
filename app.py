from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request, abort, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from logger import logger
from typing import Optional

from model import db_url, engine
from schemas import *
from model.tag_termo import TagTermo
from model.categoria_tag import CategoriaTag
from model.termo_compromisso import TermoCompromisso
from model.termos_registrados import TermosRegistrados
from model.atividades_registradas import AtividadesRegistradas  
from model.scraping import function_scraping_cvm
from model.chatgpt import consolidado_resumo_chatgpt

info = Info(title="API de Controle e Classificação de Termos de Compromisso da CVM (MVP - Sprint 1)", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)

CORS(app)

# definindo tags
doc_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
tags_tag = Tag(name="Tags", description="Adição, visualização e remoção de tags para classificar os Termos de Compromisso")
termo_tag = Tag(name="Termos de Compromisso", description="Adição, visualização e remoção de Termos de Compromisso")
atividade_tag = Tag(name="Atividades", description="Adição, visualização e remoção de Atividades")
scraping_tag = Tag(name="Scraping", description="Scraping de dados da CVM")
chatgpt_tag = Tag(name="Chat GPT", description="Usa o chatbot GPT-3.5-turbo para resumir os pareceres do Termos de Compromisso da CVM")

@app.get('/swagger', tags=[doc_tag])
def swagger():
    """Redireciona para a documentação Swagger.
    """
    return redirect('/openapi/swagger')


@app.get('/documentacao', tags=[doc_tag])
def documentacao():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.get('/get_tags', tags=[tags_tag], responses={"200": TagCategoriaList, "404": ErrorSchema})
def get_tags():
    """Retorna todas as tags cadastradas na base de dados. Traz também as informações sobre as categorias de tags, como nome e cor."""

    tag_dict = {}
    query = text("SELECT ID FROM tags_categoria")
    result = engine.execute(query)

    for row in result:
        id_categoria = row['ID']
        categoria = CategoriaTag(id_categoria)
        categoria_dict = {
            'nome_categoria': categoria.consultar_nome_categoria(),
            'cor': categoria.consultar_cor(),
            'tags': categoria.consultar_dict_tags()
        }
        tag_dict[id_categoria] = categoria_dict

    return jsonify(tag_dict)


@app.get('/get_status_termos', tags=[termo_tag], responses={"200": StatusTermos, "404": ErrorSchema})
def get_status_termos():
    """ Retorna a quantidade de termos classificados e não classificados."""

    query = text("SELECT ID FROM termos_compromisso WHERE 1")
    result = engine.execute(query).fetchall()

    lista_termos = [row[0] for row in result]
    registros = TermosRegistrados()
    
    for termo in lista_termos:
        termo_i = TermoCompromisso(termo)
        registros.registrar_termo(termo_i)
    resposta = registros.get_status_termos()
        
    return jsonify(resposta)


@app.get('/get_info_termos', tags=[termo_tag], responses={"200": Termos, "404": ErrorSchema})
def get_info_termos():
    """ Retorna todas as informações sobre os termos de compromisso cadastrados na base de dados já formatada para preenchimento da tabela de termos de compromisso."""

    query = text("SELECT ID FROM termos_compromisso WHERE 1")
    result = engine.execute(query).fetchall()

    lista_termos = [row[0] for row in result]
    registros = TermosRegistrados()
    
    for termo in lista_termos:
        termo_i = TermoCompromisso(termo)
        registros.registrar_termo(termo_i)
    resposta = registros.get_todos_termos_formatado()
        
    return jsonify(resposta)


@app.post('/add_termo', tags=[termo_tag], responses={"200": Termo, "404": ErrorSchema})
def add_termo(form: NewTermoSchema):
    """Adiciona um novo termo de compromisso à base de dados e retorna o ID do termo adicionado.
    
    Obs. O parâmetros número do processo é único. Alterar num_processo antes de rodar o teste. """

    termo = TermoCompromisso()
    id_termo = termo.adicionar_novo_termo(form)
    info_termo = TermoCompromisso(id_termo).get_termo_formatado()

    return jsonify(info_termo)


@app.post('/get_info_termo_por_id', tags=[termo_tag], responses={"200": Termo, "404": ErrorSchema})
def get_info_termo_por_id(form: InputIDTermoSchema):
    """Retorna todas as informações sobre um termo de compromisso especifico (id_termo). """
    termo = TermoCompromisso(form.id_termo)
    info_termo = termo.get_termo_formatado()

    return jsonify(info_termo)


@app.post('/get_atividades', tags=[atividade_tag], responses={"200": AtividadesRegistradasSchema, "404": ErrorSchema})
def get_atividades(form: InputAtividadesRegistradas):
    """ Retorna todas as atividades registradas na base de dados já formatada para preenchimento da linha do tempo das atividades.
    É possível escolher o número de atividades que deseja que retorne e/ou as atividades relacionadas ao id de um termo de compromisso especifico ."""

    resposta = AtividadesRegistradas().consultar_atividades_formatado(form.n_atividades, form.id_termo)
        
    return jsonify(resposta)


@app.post('/cadastrar_nova_categoria', tags=[tags_tag],  responses={"200": IDCategoriaSchema, "404": ErrorSchema})
def cadastrar_nova_categoria(form: CadastraCategoriaTagSchema):
    """ Cadastrar uma nova categoria de tags e retorna ID da categoria cadastrada."""

    id_categoria = CategoriaTag().adicionar_categoria_tag(form)

    return jsonify(id_categoria)


@app.post('/cadastrar_nova_tag', tags=[tags_tag],  responses={"200": IDTagSchema, "404": ErrorSchema})
def cadastrar_nova_tag(form: CadastraTagSchema):
    """ Cadastrar uma nova tag e retorna ID da tag cadastrada."""

    id_tag = TagTermo().cadastra_nova_tag(form)
    tag_info = TagTermo(id_tag).get_tag_info()

    return jsonify(tag_info)


@app.post('/inserir_tag_termo', tags=[tags_tag],  responses={"200": InfoTagTermoSchema, "404": ErrorSchema})
def inserir_tag_termo(form: InsereTagSchema):
    """ Insere nova tag em um termo de compromisso e retorna ID do relacionamento entre a tag e o termo de compromisso."""

    id_relacionamento = TagTermo().insere_novo_relacionamento_tag_termo(form)
    tag_info = TagTermo(form.id_tag).get_tag_info_com_relacionamento(id_relacionamento)
    atualizar_status_termo = TermoCompromisso(form.id_termo).update_status_termo()
   
    return jsonify(tag_info)


@app.delete('/delete_relacionamento_tag_termo', tags=[tags_tag], responses={"200": RelacionamentoTagTermoSchema, "404": ErrorSchema})
def delete_relacionamento_tag_termo(form: TagDeleteRequest):
    """ Deleta um relacionamento entre uma tag e um termo de compromisso e retorna o ID da tag deletada."""

    id_tag = TagTermo().get_tag_info_por_id_relacionamento(form.id_relacionamento)
    tag_info = TagTermo(id_tag).get_tag_info_com_relacionamento(form.id_relacionamento)
    id_delete = TagTermo().delete_relacionamento_tag_termo(form.id_relacionamento)
    return jsonify(tag_info)


@app.post('/inserir_atividade', tags=[atividade_tag],  responses={"200": AtividadesRegistradasSchema, "404": ErrorSchema})
def inserir_atividade(form: InserirAtividadeSehema):
    """ Cadastrar uma nova tag e retorna ID da tag cadastrada."""
    user_name = form.user_name
    descricao =  form.descricao
    relacionamentos = form.relacionamentos

    if relacionamentos is not None and relacionamentos != "":
        relacionamentos_str = form.relacionamentos
        relacionamentos_list_str = relacionamentos_str.split(',')
        relacionamentos_list = [int(termo) for termo in relacionamentos_list_str if termo]
        
        id_atividade = AtividadesRegistradas().adicionar_atividade(user_name, descricao, relacionamentos_list)
    else:
        id_atividade = AtividadesRegistradas().adicionar_atividade(user_name, descricao, None)

    resposta = AtividadesRegistradas().consultar_atividades_formatado(None, None, id_atividade)

    return jsonify(resposta)


@app.delete('/delete_atividade_termo', tags=[atividade_tag], responses={"200": TagDeleteAtividade, "404": ErrorSchema})
def delete_atividade_termo(form: TagDeleteAtividade):
    """ Deleta uma atividade e retorna o ID da atividade deletada."""

    id_atividade = AtividadesRegistradas().delete_atividade(form.id_atividade)
  
    return jsonify(id_atividade)


@app.delete('/delete_termo_compromisso', tags=[termo_tag], responses={"200": TagDeleteTermo, "404": ErrorSchema})
def delete_termo_compromisso(form: TagDeleteTermo):
    """ Deleta um termo de compromisso e retorna o ID do termo deletado."""

    id_termo = TermoCompromisso(form.id_termo).delete_termo()
  
    return jsonify(id_termo)


@app.post('/editar_termo_banco', tags=[termo_tag],  responses={"200": IDTermoSchema, "404": ErrorSchema})
def editar_termo_banco(form: EditarTermoSchema):
    """ Edita informações de um termo de compromisso e retorna ID do termo editado. Se considerar o ID do termo, todos os demais campos são opcionais."""
    
    termo = TermoCompromisso(form.id_termo).editar_termo(form.num_processo, form.data_aprovacao, form.data_assinatura, form.data_publicacao, form.compromitentes, form.URL_decisao, form.data_arquivamento, form.URL_parecer, form.resumo)
    
    return jsonify(termo)


@app.get('/scraping_cvm', tags=[scraping_tag],  responses={"200": RespostaScrapingCVMSchema, "404": ErrorSchema})
def scraping_cvm():
    """ Cadastrar uma nova tag e retorna ID da tag cadastrada."""
    
    resposta_scraping = function_scraping_cvm()

    return jsonify(resposta_scraping)


@app.post('/resumir_texto_chatgpt', tags=[chatgpt_tag],  responses={"200": RespostaChatGPTSchema, "404": ErrorSchema})
def resumir_texto_chatgpt(form: ResumoChatGPTSchema):
    """ Resume pareceres dos Termos de Compromisso da CVM utilizando o modelo ChatGPT e retorna o resumo do texto."""

    resumo = consolidado_resumo_chatgpt(form.key, form.url)
    termo_resumo = TermoCompromisso(form.id_termo).update_resumo_termo(resumo)
    
    return jsonify(resumo)
