from seguridad import generar_password_hash, verificar_password


def test_password_correcto():
    password = "mi-password-seguro"

    password_hash = generar_password_hash(password)

    assert password_hash != password
    assert verificar_password(password, password_hash) is True


def test_password_incorrecto():
    password_hash = generar_password_hash("password-correcto")

    assert verificar_password(
        "password-incorrecto",
        password_hash,
    ) is False