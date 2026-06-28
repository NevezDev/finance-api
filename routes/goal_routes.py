from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import auth_utils
from database import get_db
from models.goal import Goal
from models.user import User
from schemas.goal_schema import GoalCreate

router = APIRouter(prefix="/api/goals", tags=["Metas"])


@router.get("")
def listar(db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    return db.query(Goal).filter(Goal.user_id == current_user.id).all()


@router.post("")
def criar(dados: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    meta = Goal(**dados.model_dump(), user_id=current_user.id)
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


@router.put("/{id}")
def atualizar(id: int, dados: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    meta = db.query(Goal).filter(Goal.id == id, Goal.user_id == current_user.id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta nao encontrada")

    for key, value in dados.model_dump().items():
        setattr(meta, key, value)

    db.commit()
    db.refresh(meta)
    return meta


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    meta = db.query(Goal).filter(Goal.id == id, Goal.user_id == current_user.id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta nao encontrada")

    db.delete(meta)
    db.commit()
    return {"msg": "Meta deletada"}
