import bcrypt

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_ALGORITHM = "HS256"
JWT_EXPIRACION_MINUTOS = 60


def crear_token_acceso(usuario_id: int) -> str:
    secreto = os.getenv("JWT_SECRET")

    if not secreto:
        raise RuntimeError("Falta configurar JWT_SECRET.")

    ahora = datetime.now(timezone.utc)

    contenido = {
        # sub identifica al usuario propietario del token.
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(
            minutes=JWT_EXPIRACION_MINUTOS
        ),
    }

    return jwt.encode(
        contenido,
        secreto,
        algorithm=JWT_ALGORITHM,
    )


def generar_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")

    # bcrypt admite como máximo 72 bytes.
    if len(password_bytes) > 72:
        raise ValueError(
            "La contraseña no puede superar 72 bytes."
        )

    hash_bytes = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12),
    )

    return hash_bytes.decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False

def decodificar_token_acceso(token: str) -> int:
    secreto = os.getenv("JWT_SECRET")

    if not secreto:
        raise RuntimeError("Falta configurar JWT_SECRET.")

    contenido = jwt.decode(
        token,
        secreto,
        algorithms=[JWT_ALGORITHM],
    )

    usuario_id = contenido.get("sub")

    if usuario_id is None:
        raise jwt.InvalidTokenError(
            "El token no contiene un usuario."
        )

    try:
        usuario_id = int(usuario_id)
    except (TypeError, ValueError) as error:
        raise jwt.InvalidTokenError(
            "El identificador del token no es válido."
        ) from error

    if usuario_id <= 0:
        raise jwt.InvalidTokenError(
            "El identificador del token no es válido."
        )

    return usuario_id