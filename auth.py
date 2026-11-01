import jwt
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from sqlalchemy.orm import Session

SECRET_KEY = "connectplus_super_secret_key_jwt"
ALGORITHM = "HS256"

# Configura o OAuth2 para extrair o token do header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
  to_encode = data.copy()
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=(
          "Could not validate credentials or user not authenticated. (RN01)"
      ),
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
      raise credentials_exception
  except jwt.PyJWTError:
    raise credentials_exception

  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise credentials_exception
  return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
  if current_user.role != "administrador":
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado: Apenas administradores podem realizar esta operação. (RN02/RN03)",
    )
  return current_user