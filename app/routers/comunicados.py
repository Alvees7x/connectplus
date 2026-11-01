from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import somente_admin, usuario_atual

router = APIRouter(prefix="/comunicados", tags=["Comunicados"])


def _buscar(db: Session, comunicado_id: int) -> models.Comunicado:
    comunicado = db.get(models.Comunicado, comunicado_id)
    if comunicado is None:  # RN05
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comunicado não encontrado.")
    return comunicado


@router.post(
    "", response_model=schemas.ComunicadoOut, status_code=status.HTTP_201_CREATED,
    summary="RF03 - Publicar comunicado (admin)",
)
def publicar(
    dados: schemas.ComunicadoCreate,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(somente_admin),
):
    # RN06 / RF07: o autor vem do token, nunca do corpo da requisição
    comunicado = models.Comunicado(titulo=dados.titulo, conteudo=dados.conteudo, autor_id=admin.id)
    db.add(comunicado)
    db.commit()
    db.refresh(comunicado)
    return comunicado


@router.get(
    "", response_model=list[schemas.ComunicadoOut],
    summary="RF04 - Listar comunicados (autenticado)",
)
def listar(db: Session = Depends(get_db), _: models.Usuario = Depends(usuario_atual)):
    stmt = select(models.Comunicado).order_by(models.Comunicado.data_publicacao.desc())
    return db.scalars(stmt).all()


@router.get(
    "/{comunicado_id}", response_model=schemas.ComunicadoOut,
    summary="RF04 - Consultar comunicado por ID (autenticado)",
)
def consultar(
    comunicado_id: int, db: Session = Depends(get_db), _: models.Usuario = Depends(usuario_atual)
):
    return _buscar(db, comunicado_id)


@router.put(
    "/{comunicado_id}", response_model=schemas.ComunicadoOut,
    summary="RF05 - Atualizar comunicado (admin)",
)
def atualizar(
    comunicado_id: int,
    dados: schemas.ComunicadoUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(somente_admin),
):
    comunicado = _buscar(db, comunicado_id)
    comunicado.titulo = dados.titulo      # autor e data permanecem intactos (RF07)
    comunicado.conteudo = dados.conteudo
    db.commit()
    db.refresh(comunicado)
    return comunicado


@router.delete(
    "/{comunicado_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="RF06 - Remover comunicado (admin)",
)
def remover(
    comunicado_id: int, db: Session = Depends(get_db), _: models.Usuario = Depends(somente_admin)
):
    db.delete(_buscar(db, comunicado_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
