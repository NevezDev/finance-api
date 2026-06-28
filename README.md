# Finance API

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/github/actions/workflow/status/NevezDev/finance-api/tests.yml?label=tests)
![License](https://img.shields.io/badge/license-MIT-green)

Aplicacao full stack de controle financeiro pessoal, com API REST em FastAPI e
interface desktop em Flet. Cada usuario possui seu proprio espaco para organizar
receitas, despesas, categorias e metas financeiras.



## Funcionalidades

- Cadastro e login com JWT.
- CRUD de categorias financeiras.
- CRUD de transacoes de receita e despesa.
- CRUD de metas financeiras.
- Relatorio com saldo, total de receitas, total de despesas, gastos por categoria e progresso das metas.
- Dados isolados por usuario autenticado.
- Documentacao automatica da API via Swagger em `/docs`.
- Frontend desktop em Flet.
- Testes automatizados e CI com GitHub Actions.
- Imagem Docker para executar a API.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT com `python-jose`
- Passlib/bcrypt para hash de senhas
- Pydantic
- Flet
- PostgreSQL opcional via `DATABASE_URL`

## Como Rodar Localmente

Requer Python 3.12 ou superior.

1. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Configure as variaveis de ambiente:

```bash
copy .env.example .env
```

4. Inicie a API:

```bash
uvicorn main:app --reload
```

5. Em outro terminal, inicie o frontend Flet:

```bash
python frontend.py
```

6. Acesse a documentacao:

```text
http://127.0.0.1:8000/docs
```

O frontend consome a API em `http://127.0.0.1:8000`. Mantenha o backend rodando antes de abrir a interface.
O endereco pode ser alterado pela variavel `API_BASE_URL` no `.env`.

## Testes

```bash
pip install -r requirements-dev.txt
pytest --cov=. --cov-report=term-missing
```

Os testes cobrem autenticacao, autorizacao, isolamento entre usuarios e o fluxo
de receitas, despesas, categorias e metas.

## Docker

```bash
docker build -t finance-api .
docker run --env-file .env -p 8000:8000 finance-api
```

Em producao, use uma URL persistente em `DATABASE_URL`; o SQLite interno do
container nao deve ser tratado como armazenamento permanente.

## Banco De Dados

Por padrao, o projeto usa SQLite local:

```env
DATABASE_URL=sqlite:///./finance.db
```

Para usar PostgreSQL, altere a variavel no `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

## Principais Rotas

```text
POST   /api/auth/register
POST   /api/auth/login

GET    /api/categories
POST   /api/categories
PUT    /api/categories/{id}
DELETE /api/categories/{id}

GET    /api/transactions
POST   /api/transactions
PUT    /api/transactions/{id}
DELETE /api/transactions/{id}

GET    /api/goals
POST   /api/goals
PUT    /api/goals/{id}
DELETE /api/goals/{id}

GET    /api/reports/summary
GET    /api/health
```

## Exemplos De Uso

### Cadastro

```json
{
  "full_name": "Maria Silva",
  "email": "maria@email.com",
  "password": "123456"
}
```

### Categoria

```json
{
  "name": "Alimentacao",
  "type": "despesa",
  "color": "#ef4444"
}
```

### Transacao

```json
{
  "category_id": 1,
  "description": "Mercado",
  "type": "despesa",
  "amount": 180.5,
  "transaction_date": "2026-06-25",
  "payment_method": "cartao",
  "notes": "Compra da semana"
}
```

### Meta

```json
{
  "title": "Reserva de emergencia",
  "target_amount": 5000,
  "current_amount": 1200,
  "deadline": "2026-12-31",
  "status": "ativa"
}
```

## Estrutura

```text
finance_api/
|-- main.py
|-- database.py
|-- auth_utils.py
|-- models/
|-- routes/
|-- schemas/
|-- tests/
|-- .github/workflows/tests.yml
|-- frontend.py
|-- Dockerfile
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Regras De Negocio

- Receitas aumentam o saldo e despesas reduzem o saldo.
- Gastos por categoria consideram somente despesas.
- O progresso de metas ativas utiliza o saldo positivo disponivel.
- Metas pausadas ou concluidas utilizam seu valor atual salvo.
- Cada usuario acessa somente os proprios registros.

## Proximos Passos

- Adicionar migracoes com Alembic.
- Criar filtros por periodo e exportacao CSV.
- Implementar recuperacao de senha.
- Publicar uma demonstracao online.

## Aprendizados

Este projeto demonstra fundamentos importantes para uma vaga junior: API REST, autenticacao, persistencia com ORM, separacao por camadas, validacao de dados, regras simples de negocio e rotas de relatorio.

## Licenca

Distribuido sob a licenca MIT. Consulte [LICENSE](LICENSE).
