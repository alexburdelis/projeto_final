from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Configuração do banco de dados dinâmica
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:admin@localhost:5433/streamflix"  
)

engine = create_engine(DATABASE_URL) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db(): # Função para obter uma sessão do banco de dados
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
