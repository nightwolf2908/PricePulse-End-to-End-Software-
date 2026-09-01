from decimal import Decimal

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def extraer_precio(url, *, headless=True):
    """Extrae los datos de una ficha de producto de Books to Scrape."""

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=headless)

        try:
            pagina = navegador.new_page()

            respuesta = pagina.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            if respuesta is None or not respuesta.ok:
                estado = respuesta.status if respuesta else "sin respuesta"
                raise RuntimeError(
                    f"No se pudo cargar el producto: {estado}"
                )

            pagina.locator(
                ".product_main .price_color"
            ).wait_for(timeout=10000)

            soup = BeautifulSoup(pagina.content(), "html.parser")

            titulo = soup.select_one(".product_main h1")
            precio = soup.select_one(".product_main .price_color")

            if titulo is None or precio is None:
                raise ValueError(
                    "La página no contiene un título y un precio."
                )

            nombre = titulo.get_text(strip=True)
            texto_precio = precio.get_text(strip=True)

            if not nombre:
                raise ValueError("El título del producto está vacío.")

            if not texto_precio.startswith("£"):
                raise ValueError(
                    f"Moneda inesperada: {texto_precio}"
                )

            precio_decimal = Decimal(
                texto_precio.removeprefix("£").strip()
            )

            if not precio_decimal.is_finite() or precio_decimal < 0:
                raise ValueError("El precio no es válido.")

            return {
                "nombre": nombre,
                "precio": precio_decimal,
                "moneda": "GBP",
                "url": url,
            }

        finally:
            navegador.close()