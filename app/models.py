from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def agora():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))  # "administrador" | "colaborador"

    comunicados: Mapped[list["Comunicado"]] = relationship(back_populates="autor")


class Comunicado(Base):
    __tablename__ = "comunicados"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    conteudo: Mapped[str] = mapped_column(Text)
    data_publicacao: Mapped[datetime] = mapped_column(DateTime, default=agora)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    autor: Mapped[Usuario] = relationship(back_populates="comunicados")
