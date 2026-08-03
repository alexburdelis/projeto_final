from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database.connection import get_db
from database.models import Usuario
from security.auth import verificar_senha, gerar_hash_senha, criar_token_acesso

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Validador com EmailStr 
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr 
    senha: str

@router.post("/cadastrar")
def cadastrar_usuario(request: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    novo_usuario = Usuario(
        nome=request.nome, 
        email=request.email, 
        hashed_password=gerar_hash_senha(request.senha)
    )
    db.add(novo_usuario)
    db.commit()
    return {"message": "Usuário criado com sucesso!"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #form_data - faz a validação do email e senha, e joga na variável
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    token = criar_token_acesso(data={"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}