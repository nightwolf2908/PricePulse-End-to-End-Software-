from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from sqlalchemy.exc import OperationalError
from notificaciones import enviar_alerta_si_corresponde

import models
from celery_app import celery_app
from database import SessionLocal
from scraper import ErrorTemporalScraping, extraer_precio


@celery_app.task
def sumar(numero_a, numero_b):
    return numero_a + numero_b


@celery_app.task(
    autoretry_for=(
        PlaywrightTimeoutError,
        ErrorTemporalScraping,
        OperationalError,
    ),
    retry_kwargs={"max_retries": 3},
    retry_backoff=10,
    retry_jitter=False,
)
def revisar_producto(producto_id):
    # Obtener la URL sin mantener la conexión durante el scraping.
    db = SessionLocal()

    try:
        producto = db.get(
            models.ProductoMonitoreado,
            producto_id,
        )

        if producto is None:
            return {
                "estado": "omitido",
                "motivo": "producto_no_existe",
                "producto_id": producto_id,
            }

        if not producto.activo:
            return {
                "estado": "omitido",
                "motivo": "producto_inactivo",
                "producto_id": producto_id,
            }

        url = producto.url

    finally:
        db.close()

    datos = extraer_precio(url, headless=True)

    db = SessionLocal()

    try:
        producto = db.get(
            models.ProductoMonitoreado,
            producto_id,
        )

        if producto is None or not producto.activo:
            return {
                "estado": "omitido",
                "motivo": "producto_eliminado_o_inactivo",
                "producto_id": producto_id,
            }

        observacion = models.HistorialPrecio(
            producto_id=producto.id,
            precio=datos["precio"],
        )

        producto.nombre = datos["nombre"]
        producto.imagen_url = datos["imagen_url"]

        db.add(observacion)
        db.commit()
        db.refresh(observacion)

        # Comprobar si este producto ya generó una alerta.
        alerta_existente = (
            db.query(models.AlertaEnviada)
            .filter(
                models.AlertaEnviada.producto_id
                == producto.id
            )
            .first()
        )

        if alerta_existente is not None:
            estado_alerta = "enviada_anteriormente"

        elif datos["precio"] > producto.precio_objetivo:
            estado_alerta = "precio_superior_al_objetivo"

        else:
            resultado_notificacion = (
                enviar_alerta_si_corresponde(
                    producto={
                        "nombre": datos["nombre"],
                        "precio": datos["precio"],
                        "moneda": datos["moneda"],
                        "url": datos["url"],
                    },
                    precio_objetivo=producto.precio_objetivo,
                    destinatario=producto.usuario.email,
                )
            )

            alerta = models.AlertaEnviada(
                producto_id=producto.id,
                precio=datos["precio"],
            )

            db.add(alerta)
            db.commit()

            estado_alerta = resultado_notificacion["estado"]

        return {
            "estado": "actualizado",
            "producto_id": producto.id,
            "historial_id": observacion.id,
            "nombre": producto.nombre,
            "precio": str(observacion.precio),
            "moneda": datos["moneda"],
            "fecha_registro": (
                observacion.fecha_registro.isoformat()
            ),
            "alerta": estado_alerta,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task
def programar_revisiones():
    """
    Busca todos los productos activos y crea una tarea
    independiente para cada uno.
    """

    db = SessionLocal()

    try:
        productos_ids = [
            producto_id
            for (producto_id,) in (
                db.query(models.ProductoMonitoreado.id)
                .filter(
                    models.ProductoMonitoreado.activo.is_(True)
                )
                .all()
            )
        ]

    finally:
        db.close()

    tareas_ids = []

    for producto_id in productos_ids:
        tarea = revisar_producto.delay(producto_id)
        tareas_ids.append(tarea.id)

    return {
        "productos_encontrados": len(productos_ids),
        "tareas_creadas": tareas_ids,
    }