import bcrypt


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