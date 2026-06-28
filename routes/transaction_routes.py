from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import auth_utils
from database import get_db
from models.category import Category
from models.transaction import Transaction
from models.user import User
from schemas.transaction_schema import TransactionCreate

router = APIRouter(prefix="/api/transactions", tags=["Transacoes"])


@router.get("")
def listar(
    type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_utils.get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if type:
        query = query.filter(Transaction.type == type)
    return query.order_by(Transaction.transaction_date.desc()).all()


@router.post("")
def criar(dados: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    if dados.category_id:
        categoria = db.query(Category).filter(Category.id == dados.category_id, Category.user_id == current_user.id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    transacao = Transaction(**dados.model_dump(), user_id=current_user.id)
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return transacao


@router.put("/{id}")
def atualizar(id: int, dados: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    transacao = db.query(Transaction).filter(Transaction.id == id, Transaction.user_id == current_user.id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transacao nao encontrada")

    if dados.category_id:
        categoria = db.query(Category).filter(Category.id == dados.category_id, Category.user_id == current_user.id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    for key, value in dados.model_dump().items():
        setattr(transacao, key, value)

    db.commit()
    db.refresh(transacao)
    return transacao


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    transacao = db.query(Transaction).filter(Transaction.id == id, Transaction.user_id == current_user.id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transacao nao encontrada")

    db.delete(transacao)
    db.commit()
    return {"msg": "Transacao deletada"}
