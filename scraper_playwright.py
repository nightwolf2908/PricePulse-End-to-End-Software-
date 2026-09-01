from decimal import Decimal

from bs4 import BeautifulSoup
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


def extraer_precio(url):
    """Obtiene el nombre, precio y moneda de un libro."""

    with sync_playwright() as p:
        # False muestra el navegador mientras aprendes.
        # Para los workers de Celery utilizaremos True.
        navegador = p.chromium.launch(headless=False)

        try:
            pagina = navegador.new_page()

            # Abre el enlace y espera a que el HTML esté disponible.
            respuesta = pagina.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            if respuesta is None or not respuesta.ok:
                estado = respuesta.status if respuesta else "sin respuesta"
                raise RuntimeError(f"No se pudo cargar el producto: {estado}")

            # Espera el precio de la ficha del producto.
            # Así evitamos una pausa fija como time.sleep(5).
            pagina.locator(
                ".product_main .price_color"
            ).wait_for(timeout=10000)

            # BeautifulSoup permite buscar elementos dentro del HTML.
            soup = BeautifulSoup(pagina.content(), "html.parser")

            titulo = soup.select_one(".product_main h1")
            precio = soup.select_one(".product_main .price_color")

            if titulo is None or precio is None:
                raise ValueError("La página no contiene un título y un precio.")

            # Ejemplo: "£51.77" → Decimal("51.77").
            texto_precio = precio.get_text(strip=True)

            if not texto_precio.startswith("£"):
                raise ValueError(f"Moneda inesperada: {texto_precio}")

            precio_decimal = Decimal(
                texto_precio.removeprefix("£").strip()
            )

            return {
                "nombre": titulo.get_text(strip=True),
                "precio": precio_decimal,
                "moneda": "GBP",
                "url": url,
            }

        finally:
            # Se ejecuta tanto si hubo éxito como si ocurrió un error.
            navegador.close()


# Este bloque solo se ejecuta al lanzar este archivo directamente.
# Importar extraer_precio desde un worker no ejecutará este ejemplo.
if __name__ == "__main__":
    url_libro = (
        "https://books.toscrape.com/"
        "catalogue/a-light-in-the-attic_1000/index.html"
    )

    try:
        producto = extraer_precio(url_libro)

        print(f"Producto: {producto['nombre']}")
        print(f"Precio: {producto['precio']} {producto['moneda']}")
        print(f"URL: {producto['url']}")

    except PlaywrightTimeoutError:
        print("Error: la página o el precio tardaron demasiado en cargar.")

    except Exception as error:
        print(f"Error al extraer el producto: {error}")