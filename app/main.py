from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from . import models
from .database import Base, SessionLocal, engine
from .routers import auth, comunicados
from .security import hash_senha

USUARIOS_INICIAIS = [
    {"nome": "Administrador ConnectPlus", "username": "admin", "senha": "admin123", "perfil": "administrador"},
    {"nome": "Colaborador ConnectPlus", "username": "colaborador", "senha": "colab123", "perfil": "colaborador"},
]


def criar_usuarios_iniciais():
    with SessionLocal() as db:
        for u in USUARIOS_INICIAIS:
            existe = db.scalar(select(models.Usuario).where(models.Usuario.username == u["username"]))
            if not existe:
                db.add(models.Usuario(
                    nome=u["nome"], username=u["username"],
                    senha_hash=hash_senha(u["senha"]), perfil=u["perfil"],
                ))
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    criar_usuarios_iniciais()
    yield


app = FastAPI(
    title="ConnectPlus - API de Comunicados Internos",
    description=(
        "Publicação e consulta de comunicados internos.\n\n"
        "**Contas de demonstração:** `admin` / `admin123` (administrador) e "
        "`colaborador` / `colab123` (colaborador).\n\n"
        "Clique em **Authorize** para se autenticar."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(comunicados.router)
