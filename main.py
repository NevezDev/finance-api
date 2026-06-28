import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import auth_routes, category_routes, goal_routes, report_routes, transaction_routes

Base.metadata.create_all(bind=engine)
load_dotenv()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]

app = FastAPI(
    title="Finance API",
    description="API para controle financeiro pessoal com receitas, despesas, categorias, metas e relatorios.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(category_routes.router)
app.include_router(transaction_routes.router)
app.include_router(goal_routes.router)
app.include_router(report_routes.router)


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
