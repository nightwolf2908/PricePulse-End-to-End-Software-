import os
from decimal import Decimal

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def enviar_alerta_si_corresponde(producto, precio_objetivo, destinatario):
    precio_actual = Decimal(str(producto["precio"]))
    objetivo = Decimal(str(precio_objetivo))

    if not precio_actual.is_finite() or not objetivo.is_finite():
        raise ValueError("Los precios deben ser números finitos.")

    if precio_actual < 0 or objetivo < 0:
        raise ValueError("Los precios no pueden ser negativos.")

    # El objetivo debe estar expresado en la moneda del producto.
    if precio_actual > objetivo:
        return {"estado": "sin_alerta"}

    mensaje = Mail(
        from_email=os.environ["SENDGRID_FROM_EMAIL"],
        to_emails=destinatario,
        subject="PricePulse: un producto alcanzó tu precio objetivo",
        plain_text_content=(
            f"Producto: {producto['nombre']}\n"
            f"Precio actual: {precio_actual} {producto['moneda']}\n"
            f"Precio objetivo: {objetivo} {producto['moneda']}\n\n"
            f"Ver producto: {producto['url']}"
        ),
    )

    cliente = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    respuesta = cliente.send(mensaje)

    if respuesta.status_code != 202:
        raise RuntimeError(
            f"Respuesta inesperada de SendGrid: {respuesta.status_code}"
        )

    return {"estado": "aceptado_por_sendgrid"}