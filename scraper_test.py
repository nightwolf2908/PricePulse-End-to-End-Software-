from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from scraper import extraer_precio


def main():
    url = (
        "https://books.toscrape.com/"
        "catalogue/a-light-in-the-attic_1000/index.html"
    )

    try:
        # Mostramos el navegador para observar la prueba.
        producto = extraer_precio(url, headless=False)

    except PlaywrightTimeoutError:
        print("ERROR: la página o el precio tardaron demasiado en cargar.")
        return 1

    except Exception as error:
        print(f"ERROR: {error}")
        return 1

    print("Extracción completada:")
    print(f"Producto: {producto['nombre']}")
    print(f"Precio: {producto['precio']} {producto['moneda']}")
    print(f"URL: {producto['url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())