from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# RN07: sem senha/hash em nenhum schema de saída
class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    username: str
    perfil: str


class _ComunicadoBase(BaseModel):
    # RN06 e RN08: campos extras (autor_id, perfil...) são rejeitados com 422
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(max_length=200, examples=["Manutenção programada"])
    conteudo: str = Field(examples=["O sistema ficará indisponível sábado das 22h às 23h."])

    # RN04: título e conteúdo obrigatórios (e não vazios/só espaços)
    @field_validator("titulo", "conteudo")
    @classmethod
    def nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("não pode ser vazio")
        return v


class ComunicadoCreate(_ComunicadoBase):
    pass


class ComunicadoUpdate(_ComunicadoBase):
    pass


class ComunicadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    conteudo: str
    data_publicacao: datetime
    autor: UsuarioOut
