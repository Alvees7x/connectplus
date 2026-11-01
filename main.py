from auth import create_access_token, get_current_user, require_admin
from database import Base, SessionLocal, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import Comunicado, User
from schemas import (
    ComunicadoCreate,
    ComunicadoResponse,
    ComunicadoUpdate,
    TokenResponse,
    UserResponse,
)
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ConnectPlus - API de Comunicados Internos (JWT & Swagger)",
    version="2.0.0",
    description="API centralizada com autenticação JWT e documentação Swagger.",
)


@app.on_event("startup")
def startup_db():
  db = SessionLocal()
  if not db.query(User).first():
    admin = User(username="admin_connect", password="123", role="administrador")
    colab = User(
        username="colaborador_joao", password="123", role="colaborador"
    )
    db.add_all([admin, colab])
    db.commit()
  db.close()


@app.post(
    "/login",
    response_model=TokenResponse,
    summary="Realizar login e obter Token JWT (Compatível com o botão Authorize do Swagger)",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
  # O OAuth2PasswordRequestForm utiliza os campos 'username' e 'password' enviados via form-data
  user = (
      db.query(User).filter(User.username == form_data.username).first()
  )
  if not user or user.password != form_data.password:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Acesso recusado: Usuário ou senha incorretos.",
    )

  access_token = create_access_token(data={"sub": user.username})
  return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/me",
    response_model=UserResponse,
    summary="Consultar informações do usuário logado (RF02)",
)
def get_my_info(current_user: User = Depends(get_current_user)):
  return current_user


@app.get(
    "/comunicados",
    response_model=list[ComunicadoResponse],
    summary="Listar comunicados (RF04)",
)
def listar_comunicados(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  return (
      db.query(Comunicado)
      .order_by(Comunicado.data_publicacao.desc())
      .all()
  )


@app.post(
    "/comunicados",
    response_model=ComunicadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar comunicado (RF03, RN04, RN06)",
)
def criar_comunicado(
    payload: ComunicadoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
  if not payload.titulo.strip() or not payload.conteudo.strip():
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Dados rejeitados: Título e conteúdo não podem ser vazios.",
    )

  novo_comunicado = Comunicado(
      titulo=payload.titulo, conteudo=payload.conteudo, autor_id=current_user.id
  )
  db.add(novo_comunicado)
  db.commit()
  db.refresh(novo_comunicado)
  return novo_comunicado


@app.put(
    "/comunicados/{comunicado_id}",
    response_model=ComunicadoResponse,
    summary="Atualizar comunicado (RF05, RN05)",
)
def atualizar_comunicado(
    comunicado_id: int,
    payload: ComunicadoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
  comunicado = (
      db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
  )
  if not comunicado:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Registro não encontrado (Comunicado inexistente).",
    )

  if payload.titulo is not None:
    comunicado.titulo = payload.titulo
  if payload.conteudo is not None:
    comunicado.conteudo = payload.conteudo

  db.commit()
  db.refresh(comunicado)
  return comunicado


@app.delete(
    "/comunicados/{comunicado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir comunicado (RF06, RN05)",
)
def excluir_comunicado(
    comunicado_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
  comunicado = (
      db.query(Comunicado).filter(Comunicado.id == comunicado_id).first()
  )
  if not comunicado:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Registro não encontrado (Comunicado inexistente).",
    )

  db.delete(comunicado)
  db.commit()
  return None