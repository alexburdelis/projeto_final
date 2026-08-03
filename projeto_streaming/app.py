from fastapi import FastAPI
from database.connection import engine
from database.models import Base
from routes.video_routes import router as video_router 
from routes.auth_routes import router as auth_router


print("Verificando/Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StreamFlix API")


app.include_router(video_router) # Inclui a rota de upload de vídeos
app.include_router(auth_router)  # Inclui a rota de autenticação (login, registro, etc.)

@app.get("/")
def root():
    return {"message": "StreamFlix API rodando!"}


