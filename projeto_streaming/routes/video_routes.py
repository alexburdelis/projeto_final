from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database.connection import get_db
from database.models import Video, TarefaProcessamento, StatusTarefa, Usuario
from mensageria.publisher import enviar_para_fila
from security.auth import get_usuario_atual

router = APIRouter(prefix="/videos", tags=["Upload de Vídeos"])

class VideoUploadRequest(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tamanho_mb: float
    formato_original: str
    formato_destino: str

@router.post("/upload")
def upload_video(
    request: VideoUploadRequest, 
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_usuario_atual) 
):
    novo_video = Video(
        titulo=request.titulo,
        descricao=request.descricao,
        tamanho_mb=request.tamanho_mb,
        formato_original=request.formato_original,
        usuario_id=usuario_logado.id 
    )
    db.add(novo_video)
    db.commit()
    db.refresh(novo_video)

    nova_tarefa = TarefaProcessamento(
        video_id=novo_video.id,
        formato_destino=request.formato_destino,
        status=StatusTarefa.PENDENTE
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)

    enviar_para_fila(tarefa_id=nova_tarefa.id, formato_destino=nova_tarefa.formato_destino)

    return {"message": f"Valeu {usuario_logado.nome}! O vídeo foi pra fila.", "tarefa_id": nova_tarefa.id}

@router.get("/relatorio")
def relatorio_processamento(db: Session = Depends(get_db)):
    tarefas = db.query(TarefaProcessamento).all()
    relatorio = []
    for t in tarefas:
        relatorio.append({
            "tarefa_id": t.id,
            "dono_do_video": t.video.dono.nome,
            "video_titulo": t.video.titulo,
            "formato_original": t.video.formato_original,
            "formato_destino": t.formato_destino,
            "status_atual": t.status,
            "atualizado_em": t.atualizado_em
        })
    return {"total_processado": len(relatorio), "dados": relatorio}