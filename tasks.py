from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from celery_app import celery_app
from scraper import ErrorTemporalScraping, extraer_precio


@celery_app.task
def sumar(numero_a, numero_b):
    return numero_a + numero_b


@celery_app.task(
    autoretry_for=(PlaywrightTimeoutError, ErrorTemporalScraping),
    retry_kwargs={"max_retries": 3},
    retry_backoff=10,
    retry_jitter=False,
)
def revisar_precio(url):
    producto = extraer_precio(url, headless=True)

    return {
        "nombre": producto["nombre"],
        "precio": str(producto["precio"]),
        "moneda": producto["moneda"],
        "url": producto["url"],
    }