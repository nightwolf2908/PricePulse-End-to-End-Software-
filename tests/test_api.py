from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_flujo_registro_login_y_usuario_actual():
    email = f"prueba-{uuid4()}@example.com"
    password = "password-seguro-123"

    respuesta_registro = client.post(
        "/usuarios",
        json={
            "email": email,
            "password": password,
        },
    )

    assert respuesta_registro.status_code == 201
    assert respuesta_registro.json()["usuario"]["email"] == email

    respuesta_login = client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert respuesta_login.status_code == 200

    token = respuesta_login.json()["access_token"]

    assert token
    assert respuesta_login.json()["token_type"] == "bearer"

    respuesta_usuario = client.get(
        "/usuarios/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert respuesta_usuario.status_code == 200
    assert respuesta_usuario.json()["email"] == email


def test_endpoint_protegido_rechaza_peticion_sin_token():
    respuesta = client.get("/usuarios/me")

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Debes iniciar sesión."