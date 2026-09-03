import jwt

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

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

from seguridad import (
    crear_token_acceso,
    generar_password_hash,
    verificar_password,
    decodificar_token_acceso,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="PricePulse API", version="0.1.0")

seguridad_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(
        seguridad_bearer
    ),
    db: Session = Depends(get_db),
):
    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="Debes iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        usuario_id = decodificar_token_acceso(
            credenciales.credentials
        )
    except (jwt.InvalidTokenError, RuntimeError):
        raise HTTPException(
            status_code=401,
            detail="El token es inválido o ha vencido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="El usuario del token ya no existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario

# Definimos qué datos "esperamos" que nos envíe el usuario desde la web (Esquema Pydantic)
class ProductoCrear(BaseModel):
    url: HttpUrl
    precio_objetivo: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

@app.post("/productos", status_code=201)
def crear_producto(
    producto: ProductoCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual),
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
        usuario_id=usuario_actual.id,
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
def listar_productos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),
):
    productos = (
        db.query(models.ProductoMonitoreado)
        .filter(
            models.ProductoMonitoreado.usuario_id
            == usuario_actual.id
        )
        .all()
    )

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
@app.get("/usuarios/me")
def obtener_mi_usuario(
    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),
):
    return {
        "id": usuario_actual.id,
        "email": usuario_actual.email,
        "fecha_creacion": usuario_actual.fecha_creacion,
    }

class LoginEntrada(BaseModel):
    email: str
    password: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(
    credenciales: LoginEntrada,
    db: Session = Depends(get_db),
):
    email_normalizado = credenciales.email.strip().lower()

    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == email_normalizado)
        .first()
    )

    # Utilizamos el mismo mensaje si falla el correo o la contraseña.
    # Así no revelamos qué correos están registrados.
    if usuario is None or not verificar_password(
        credenciales.password,
        usuario.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token_acceso(usuario.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }