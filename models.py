from datetime import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, index=True, nullable=False)
  password = Column(String, nullable=False)  # Senha armazenada (simples para exemplo)
  role = Column(String, nullable=False)  # "administrador" ou "colaborador"

  comunicados = relationship("Comunicado", back_populates="autor")


class Comunicado(Base):
  __tablename__ = "comunicados"

  id = Column(Integer, primary_key=True, index=True)
  titulo = Column(String, nullable=False)
  conteudo = Column(Text, nullable=False)
  data_publicacao = Column(DateTime, default=datetime.utcnow)
  autor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  autor = relationship("User", back_populates="comunicados")