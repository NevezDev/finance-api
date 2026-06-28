# Finance API

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/github/actions/workflow/status/NevezDev/finance-api/tests.yml?label=tests)
![License](https://img.shields.io/badge/license-MIT-green)

Uma aplicação para organizar a vida financeira em um só lugar. Ela permite registrar receitas e despesas, criar categorias, acompanhar metas e visualizar um resumo do saldo.

O projeto possui uma API REST desenvolvida com FastAPI e uma interface desktop feita com Flet. Cada usuário acessa apenas os próprios dados.

## O que é possível fazer

- Criar uma conta e entrar com autenticação JWT.
- Organizar receitas e despesas por categoria.
- Criar e acompanhar metas financeiras.
- Consultar saldo, totais e gastos por categoria.
- Acompanhar o progresso das metas.
- Usar a API pelo Swagger em `/docs`.

## Tecnologias

- Python e FastAPI
- SQLAlchemy e Pydantic
- SQLite, com suporte a PostgreSQL
- JWT e bcrypt
- Flet
- Pytest e GitHub Actions
- Docker

## Como executar

Requer Python 3.12 ou superior.

1. Crie e ative o ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie o arquivo de configuração:

```bash
copy .env.example .env
```

4. Inicie a API:

```bash
uvicorn main:app --reload
```

5. Em outro terminal, abra a interface:

```bash
python frontend.py
```

A documentação estará disponível em `http://127.0.0.1:8000/docs`.

O frontend utiliza `http://127.0.0.1:8000` por padrão. Esse endereço pode ser alterado pela variável `API_BASE_URL` no `.env`.

## Testes

```bash
pip install -r requirements-dev.txt
pytest --cov=. --cov-report=term-missing
```

Os testes cobrem autenticação, autorização, isolamento entre usuários e os principais fluxos financeiros.

## Docker

```bash
docker build -t finance-api .
docker run --env-file .env -p 8000:8000 finance-api
```

Para uso em produção, configure um banco persistente pela variável `DATABASE_URL`.

## Regras principais

- Receitas aumentam o saldo e despesas reduzem o saldo.
- O relatório por categoria considera somente despesas.
- Metas ativas usam o saldo positivo disponível no cálculo de progresso.
- Cada usuário pode acessar somente os próprios registros.

## Estrutura

```text
finance_api/
├── main.py
├── database.py
├── auth_utils.py
├── models/
├── routes/
├── schemas/
├── tests/
├── frontend.py
├── Dockerfile
└── requirements.txt
```

## Sobre o projeto

Criei este projeto para praticar a construção de uma aplicação completa, desde a modelagem do banco e as regras financeiras até a autenticação, os testes e a integração com uma interface desktop.

Algumas melhorias que ainda pretendo explorar são filtros por período, exportação CSV, recuperação de senha e uma demonstração online.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).