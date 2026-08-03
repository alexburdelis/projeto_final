from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base() 

#Enumeração para o status da tarefa
class StatusTarefa(str, enum.Enum): 
    PENDENTE = "PENDENTE"
    PROCESSANDO = "PROCESSANDO"
    CONCLUIDO = "CONCLUIDO"
    ERRO = "ERRO"

class Usuario(Base):
    __tablename__ = "usuarios" #tabela de usuários

    #uso do orm para definir os campos da tabela
    id = Column(Integer, primary_key=True, index=True) 
    nome = Column(String(80), nullable=False)
    email = Column(String(50), unique=True, index = True, nullable=False)
    plano = Column(String(10), default="FREE") # FREE ou PREMIUM
    
    hashed_password = Column(String(255), nullable=False) 
    criado_em = Column(DateTime, default=datetime.now)
    ativo = Column(Boolean, default=True)
    # Relacionamento: 1 Usuário -> N Vídeos
    videos = relationship("Video", back_populates="dono", cascade="all, delete-orphan") 
#os parâmetros do relacionamento indicam que se um usuário for deletado, todos os vídeos dele também serão deletados
#back_populates indica que a relação é bidirecional, ou seja, podemos acessar o dono de um vídeo a partir do vídeo e vice-versa. "dono" é o nome do atributo que será usado no modelo Video para acessar o usuário dono do vídeo.


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)

    descricao = Column(String(500), nullable=True)
    tamanho_mb = Column(Float, nullable=False) 

    formato_original = Column(String(10), nullable=False)
    data_upload = Column(DateTime, default=datetime.now)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Relacionamentos
    dono = relationship("Usuario", back_populates="videos")
    tarefas = relationship("TarefaProcessamento", back_populates="video", cascade="all, delete-orphan")

class TarefaProcessamento(Base):
    __tablename__ = "tarefas_processamento"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    formato_destino = Column(String(10), nullable=False)
    status = Column(Enum(StatusTarefa), default=StatusTarefa.PENDENTE)
    mensagem_log = Column(String(255), nullable=True) # Para guardar erros do RabbitMQ
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamento
    video = relationship("Video", back_populates="tarefas") # Relaciona a tarefa com o vídeo
