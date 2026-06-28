from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import auth_utils
from database import get_db
from models.category import Category
from models.user import User
from schemas.category_schema import CategoryCreate

router = APIRouter(prefix="/api/categories", tags=["Categorias"])


@router.get("")
def listar(db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    return db.query(Category).filter(Category.user_id == current_user.id).all()


@router.post("")
def criar(dados: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    categoria = Category(**dados.model_dump(), user_id=current_user.id)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{id}")
def atualizar(id: int, dados: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    categoria = db.query(Category).filter(Category.id == id, Category.user_id == current_user.id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    for key, value in dados.model_dump().items():
        setattr(categoria, key, value)

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    categoria = db.query(Category).filter(Category.id == id, Category.user_id == current_user.id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    db.delete(categoria)
    db.commit()
    return {"msg": "Categoria deletada"}
