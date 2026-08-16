from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext

# 1. PEGA AQUÍ TU CADENA DE CONEXIÓN DE SUPABASE
DATABASE_URL = "postgresql://postgres:TU_CONTRASEÑA@db.xxx.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic
class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    password: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

# Modelos de Base de Datos (SQLAlchemy)
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

# RUTAS DE AUTENTICACIÓN

@app.post("/api/registro")
def registrar(usuario: UsuarioRegistro, db: Session = Depends(get_db)):
    # Validar si el email ya existe
    existe = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    # Encriptar contraseña y guardar usuario
    hashed_pwd = pwd_context.hash(usuario.password)
    nuevo_usuario = UsuarioDB(nombre=usuario.nombre, email=usuario.email, password_hash=hashed_pwd)
    
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario registrado exitosamente"}

@app.post("/api/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == datos.email).first()
    if not usuario or not pwd_context.verify(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    return {
        "mensaje": "Inicio de sesión correcto",
        "usuario_id": usuario.id,
        "nombre": usuario.nombre
    }
@app.get("/")
def home():
    return {"mensaje": "API de Control de Gastos activa y funcionando correctamente"}

# Connect to Postgres via the shared transaction-mode pooler (IPv4-only)
DATABASE_URL="postgresql://postgres.kcjacyxeunhrupufdwbm:Gema.Reyes#23@aws-0-us-west-2.pooler.supabase.com:6543/postgres?pgbouncer=true"

# Connect to Postgres via the shared session-mode pooler (used for migrations)
DIRECT_URL="postgresql://postgres.kcjacyxeunhrupufdwbm:Gema.Reyes#23@aws-0-us-west-2.pooler.supabase.com:5432/postgres"