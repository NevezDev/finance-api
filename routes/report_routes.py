from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import auth_utils
from database import get_db
from models.category import Category
from models.goal import Goal
from models.transaction import Transaction
from models.user import User

router = APIRouter(prefix="/api/reports", tags=["Relatorios"])


@router.get("/summary")
def resumo(db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    transacoes = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    metas = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    categorias = db.query(Category).filter(Category.user_id == current_user.id).all()

    total_receitas = sum(t.amount for t in transacoes if t.type == "receita")
    total_despesas = sum(t.amount for t in transacoes if t.type == "despesa")
    saldo = total_receitas - total_despesas

    gastos_por_categoria = []
    for categoria in categorias:
        total = sum(
            t.amount
            for t in transacoes
            if t.type == "despesa" and t.category_id == categoria.id
        )
        if total > 0:
            gastos_por_categoria.append({
                "category": categoria.name,
                "color": categoria.color,
                "total": total,
            })

    progresso_metas = []
    for meta in metas:
        valor_atual = meta.current_amount
        if meta.status == "ativa":
            valor_atual = max(saldo, 0)

        percentual = 0
        if meta.target_amount > 0:
            percentual = round((valor_atual / meta.target_amount) * 100, 2)
        progresso_metas.append({
            "id": meta.id,
            "title": meta.title,
            "target_amount": meta.target_amount,
            "current_amount": valor_atual,
            "saved_current_amount": meta.current_amount,
            "progress_percent": percentual,
            "deadline": meta.deadline,
            "status": meta.status,
        })

    return {
        "total_income": total_receitas,
        "total_expenses": total_despesas,
        "balance": saldo,
        "transaction_count": len(transacoes),
        "active_goals": len([m for m in metas if m.status == "ativa"]),
        "expenses_by_category": gastos_por_categoria,
        "goals_progress": progresso_metas,
    }
