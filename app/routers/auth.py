from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import usuario_atual
from ..security import criar_token, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=schemas.Token, summary="RF01 - Acessar o sistema")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.scalar(select(models.Usuario).where(models.Usuario.username == form.username))
    if usuario is None or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=criar_token(usuario.id))


@router.get("/me", response_model=schemas.UsuarioOut, summary="RF02 - Dados do usuário logado")
def me(usuario: models.Usuario = Depends(usuario_atual)):
    return usuario
