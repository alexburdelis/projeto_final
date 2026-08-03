from pydantic import BaseModel
from typing import Optional


class VideoUploadRequest(BaseModel):
    #usuario_id: int
    titulo: str
    descricao: Optional[str] = None
    tamanho_mb: float
    formato_original: str
    formato_destino: str