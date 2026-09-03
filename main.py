from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from sqlalchemy.exc import IntegrityError


# Importamos la conexión y nuestros modelos
from database import get_db
import models

import logging
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, HttpUrl
from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)
from sqlalchemy.exc import SQLAlchemyError

from scraper import ErrorTemporalScraping, extraer_precio

from seguridad import generar_password_hash

logger = logging.getLogger(__name__)

app = FastAPI(title="PricePulse API", version="0.1.0")

# Definimos qué datos "esperamos" que nos envíe el usuario desde la web (Esquema Pydantic)
class ProductoCrear(BaseModel):
    url: HttpUrl
    precio_objetivo: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    usuario_id: int = Field(gt=0)

@app.post("/productos", status_code=201)
def crear_producto(
    producto: ProductoCrear,
    db: Session = Depends(get_db),
):
    # Esta integración admite únicamente nuestra tienda de práctica.
    if (
        producto.url.host != "books.toscrape.com"
        or producto.url.scheme != "https"
        or producto.url.port not in (None, 443)
        or producto.url.username is not None
        or producto.url.password is not None
    ):
        raise HTTPException(
            status_code=422,
            detail="Utiliza un enlace HTTPS de books.toscrape.com.",
        )

    usuario = db.get(models.Usuario, producto.usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="El usuario indicado no existe.",
        )

    # Primero obtenemos los datos. Si falla, no creamos el producto.
    try:
        datos = extraer_precio(str(producto.url), headless=True)

    except PlaywrightTimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="La tienda tardó demasiado en responder. Intenta después.",
        ) from error

    except ErrorTemporalScraping as error:
        raise HTTPException(
            status_code=503,
            detail="La tienda no está disponible temporalmente.",
        ) from error

    except (
        PlaywrightError,
        ValueError,
        RuntimeError,
        InvalidOperation,
    ) as error:
        logger.exception("No se pudieron extraer los datos del producto.")
        raise HTTPException(
            status_code=502,
            detail="No se pudieron obtener los datos de esa página.",
        ) from error

    nuevo_producto = models.ProductoMonitoreado(
        usuario_id=producto.usuario_id,
        url=datos["url"],
        precio_objetivo=producto.precio_objetivo,
        nombre=datos["nombre"],
        imagen_url=datos["imagen_url"],
        activo=True,
    )

    try:
        db.add(nuevo_producto)

        # Ejecuta el INSERT y obtiene el ID sin confirmar todavía.
        db.flush()

        primera_observacion = models.HistorialPrecio(
            producto_id=nuevo_producto.id,
            precio=datos["precio"],
        )

        db.add(primera_observacion)

        respuesta = {
            "mensaje": "Producto registrado con éxito.",
            "producto": {
                "id": nuevo_producto.id,
                "usuario_id": nuevo_producto.usuario_id,
                "nombre": nuevo_producto.nombre,
                "url": nuevo_producto.url,
                "imagen_url": nuevo_producto.imagen_url,
                "precio_objetivo": str(nuevo_producto.precio_objetivo),
                "precio_actual": str(datos["precio"]),
                "moneda": datos["moneda"],
            },
        }

        # Confirma el producto y su primera observación juntos.
        db.commit()

    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("No se pudo guardar el producto.")
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar el producto.",
        ) from error

    return respuesta

@app.get("/productos")
def listar_productos(db: Session = Depends(get_db)):
    # Trae todos los productos guardados en la tabla
    productos = db.query(models.ProductoMonitoreado).all()
    return productos

# 1. Esquema para recibir los datos del nuevo usuario
class UsuarioCrear(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)

# 2. Ruta para crear un usuario en la base de datos
@app.post("/usuarios", status_code=201)
def crear_usuario(
    usuario: UsuarioCrear,
    db: Session = Depends(get_db),
):
    try:
        password_hash = generar_password_hash(usuario.password)

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    nuevo_usuario = models.Usuario(
        email=usuario.email.strip().lower(),
        password_hash=password_hash,
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un usuario con ese correo.",
        ) from error

    return {
        "mensaje": "Usuario creado con éxito.",
        "usuario": {
            "id": nuevo_usuario.id,
            "email": nuevo_usuario.email,
            "fecha_creacion": nuevo_usuario.fecha_creacion,
        },
    }

# 3. Ruta opcional para listar usuarios y ver sus IDs
@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()

    return [
        {
            "id": usuario.id,
            "email": usuario.email,
            "fecha_creacion": usuario.fecha_creacion,
        }
        for usuario in usuarios
    ]
