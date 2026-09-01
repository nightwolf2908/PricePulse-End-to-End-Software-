from celery_app import celery_app


@celery_app.task
def sumar(numero_a, numero_b):
    return numero_a + numero_b