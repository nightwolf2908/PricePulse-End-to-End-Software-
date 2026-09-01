from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

# Importamos la conexión y nuestros modelos
from database import get_db
import models

app = FastAPI(title="PricePulse API", version="0.1.0")

# Definimos qué datos "esperamos" que nos envíe el usuario desde la web (Esquema Pydantic)
class ProductoCrear(BaseModel):
    url: str
    precio_objetivo: float
    usuario_id: int  # Temporal para el MVP antes de poner Login real

@app.post("/productos")
def crear_producto(producto: ProductoCrear, db: Session = Depends(get_db)):
    # 1. Creamos la estructura que SQLAlchemy entiende usando los datos recibidos
    nuevo_producto = models.ProductoMonitoreado(
        url=producto.url,
        precio_objetivo=producto.precio_objetivo,
        usuario_id=producto.usuario_id,
        nombre="Cargando producto...", # Temporal hasta que hagamos el Scraper
        imagen_url="https://placeholder.com" # Temporal
    )
    
    # 2. Le decimos a SQLAlchemy que lo guarde en la base de datos
    db.add(nuevo_producto)
    db.commit()      # Guarda los cambios de forma permanente
    db.refresh(nuevo_producto) # Recarga el objeto para traer el ID que Docker le asignó
    
    return {"mensaje": "¡Producto registrado con éxito!", "producto": nuevo_producto}

@app.get("/productos")
def listar_productos(db: Session = Depends(get_db)):
    # Trae todos los productos guardados en la tabla
    productos = db.query(models.ProductoMonitoreado).all()
    return productos

# 1. Esquema para recibir los datos del nuevo usuario
class UsuarioCrear(BaseModel):
    email: str
    password_hash: str # En el MVP enviaremos el texto directo, luego pondremos seguridad real

# 2. Ruta para crear un usuario en la base de datos
@app.post("/usuarios")
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    nuevo_usuario = models.Usuario(
        email=usuario.email,
        password_hash=usuario.password_hash # Temporalmente sin encriptar para la prueba rápida
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "¡Usuario creado con éxito!", "usuario": nuevo_usuario}

# 3. Ruta opcional para listar usuarios y ver sus IDs
@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()
