from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import decodificar_token

# Habilita o botão "Authorize" no Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    """RN01: exige identificação válida (token ausente/inválido/expirado -> 401)."""
    user_id = decodificar_token(token)
    usuario = db.get(models.Usuario, user_id) if user_id else None
    if usuario is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Credenciais inválidas ou expiradas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def somente_admin(usuario: models.Usuario = Depends(usuario_atual)) -> models.Usuario:
    """RN02/RN03: apenas administradores (colaborador -> 403)."""
    if usuario.perfil != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Operação permitida apenas a administradores.")
    return usuario
