from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
  id: int
  username: str
  role: str

  class Config:
    from_attributes = True


class LoginRequest(BaseModel):
  username: str
  password: str


class TokenResponse(BaseModel):
  access_token: str
  token_type: str


class ComunicadoCreate(BaseModel):
  titulo: str = Field(..., min_length=1)
  conteudo: str = Field(..., min_length=1)


class ComunicadoUpdate(BaseModel):
  titulo: Optional[str] = Field(None, min_length=1)
  conteudo: Optional[str] = Field(None, min_length=1)


class ComunicadoResponse(BaseModel):
  id: int
  titulo: str
  conteudo: str
  data_publicacao: datetime
  autor: UserResponse

  class Config:
    from_attributes = True