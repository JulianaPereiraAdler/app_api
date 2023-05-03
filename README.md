# API de Controle e Classificação de Termos de Compromisso da CVM (MVP - Sprint 1)

Esta API foi desenvolvida para entrega do MVP da Sprint 1 da Pós-Graduação em Engenharia de Software, PUC-RIO. Ela foi desenvolvida em Flask para servir uma aplicação desenvolvida em HTML, CSS e JS.

Esta API foi criada para acompanhar os Termos de Compromisso da CVM como ferramenta de auxilio as áreas de compliance de gestoras de investimentos. A sua funcionalidade principal é permitir o controle e a classificação dos termos de compromisso publicados pela CVM, garantindo que o compliance das gestoras estejam sempre atualizadas sobre o que está sendo julgado pela CVM e assim possam tomar providencias preventivas, evitando futuros erros.

Utilizando de uma função de scrapping com Beautiful Soup, a API atualiza o banco de dados automaticamente com as informações disponíveis no site https://conteudo.cvm.gov.br/termos_compromisso/index.html. Além disso, ela oferece diversas funcionalidades, incluindo a possibilidade de adicionar, editar e deletar informações, a criação de _tags_ para facilitar a busca e filtragem dos termos de compromisso, e um acompanhamento das atividades realizadas em cada termo.

Outra funcionalidade importante é a possibilidade de resumir os pareceres dos termos de compromisso publicados. Isso pode ser feito passando a chave da API do Chat GPT como parâmetro ao realizar o login na aplicação. Essa funcionalidade utiliza tecnologia de processamento de linguagem natural para resumir os pareceres e fornecer um resumo enxuto.


## Instalação e Execução
Para executar a API, é necessário ter todas as bibliotecas Python listadas no requirements.txt instaladas. 
Após clonar o repositório, abra o terminal e vá para o diretório raiz. 

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenpython -m venv .v.pypa.io/en/latest/).
> No Ambiente Windows foi utilizado o comando (python -m venv venv) para a criação do ambiente virtual e o comando (venv\Scripts\activate) para ativar o ambiente virtual.

 ```
(venv)$ pip install -r requirements.txt
```
Este comando instala as dependências/bibliotecas, descritas no arquivo requirements.txt.

Para executar a API basta executar:

```
(venv)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento, é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor automaticamente após uma mudança no código fonte.

```
(venv)$ flask run --host 0.0.0.0 --port 5000 --reload
```

Abra o endereço http://localhost:5000/#/ no navegador para verificar o status da API em execução. 


## Documentação
Toda a documentação pode ser encontrada no [Swagger](http://localhost:5000/swagger).


## Banco de dados
Caso o arquivo do banco de dados não esteja disponviel no repositório, crie as tabelas abaixo:

```
CREATE TABLE termos_compromisso (
    ID                INTEGER     PRIMARY KEY AUTOINCREMENT
                                  UNIQUE
                                  NOT NULL,
    numero_processo   TEXT        UNIQUE
                                  NOT NULL,
    data_aprovacao    DATE (10),
    data_assinatura   DATE (10),
    data_publicacao   DATE (10),
    compromitentes    TEXT,
    link_decisao      TEXT,
    data_arquivamento DATE (10),
    classificado      INTEGER (1) DEFAULT (0) 
                                  CONSTRAINT [0] NOT NULL
);
```

```
CREATE TABLE termos_compromisso_detalhes (
    ID           INTEGER PRIMARY KEY AUTOINCREMENT
                         UNIQUE
                         NOT NULL,
    ID_termo     NUMERIC REFERENCES termos_compromisso (ID) ON DELETE CASCADE
                                                            ON UPDATE CASCADE
                         NOT NULL,
    link_parecer TEXT,
    resumo       TEXT
);

```

```
CREATE TABLE tags_categoria (
    ID             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_categoria TEXT    UNIQUE,
    cor            TEXT
);

```

```
CREATE TABLE tags_info (
    ID           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tag     TEXT,
    ID_categoria         REFERENCES tags_categoria (ID) ON DELETE CASCADE
                                                        ON UPDATE CASCADE
);
```

```
CREATE TABLE relacionamento_tags_termos (
    ID       INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_termo         REFERENCES termos_compromisso (ID) ON DELETE CASCADE
                                                        ON UPDATE CASCADE,
    ID_tag           REFERENCES tags_info (ID) ON DELETE CASCADE
                                               ON UPDATE CASCADE
);
```

```
CREATE TABLE atividades (
    ID        INTEGER   PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    descricao           NOT NULL,
    timestamp TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) 
                        NOT NULL
);
```

```
CREATE TABLE relacionamento_atividades_termos (
    ID           INTEGER PRIMARY KEY AUTOINCREMENT,
    id_termo             REFERENCES termos_compromisso (ID) ON DELETE CASCADE
                                                            ON UPDATE CASCADE,
    id_atividade         REFERENCES atividades (ID) ON DELETE CASCADE
                                                    ON UPDATE CASCADE
);
```

Salve um arquivo chamado db.sqlite3 e salve dentro da pasta database.