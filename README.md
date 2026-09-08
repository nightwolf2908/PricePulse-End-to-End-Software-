# PricePulse

[![Pruebas de PricePulse](https://github.com/nightwolf2908/PricePulse-End-to-End-Software-/actions/workflows/ci.yml/badge.svg)](https://github.com/nightwolf2908/PricePulse-End-to-End-Software-/actions/workflows/ci.yml)

PricePulse es un MVP de monitoreo automático de precios desarrollado para aprender el proceso completo de construcción y despliegue de software.

La aplicación permite crear una cuenta, iniciar sesión y registrar productos de [Books to Scrape](https://books.toscrape.com/). Un proceso en segundo plano consulta sus precios periódicamente y envía una alerta por correo cuando alcanzan el objetivo indicado por el usuario.

**Aplicación:** [https://abdiel2908.com](https://abdiel2908.com)

## Funcionalidades

- Registro de usuarios.
- Inicio de sesión con tokens JWT.
- Contraseñas protegidas con bcrypt.
- Rutas privadas asociadas al usuario autenticado.
- Registro de productos mediante su URL.
- Extracción de nombre, imagen y precio con Playwright y BeautifulSoup.
- Almacenamiento del historial de precios.
- Procesamiento asíncrono mediante Celery.
- Programación de revisiones cada cuatro horas con Celery Beat.
- Reintentos automáticos ante errores temporales.
- Notificaciones por correo mediante SendGrid.
- Migraciones automáticas con Alembic.
- Interfaz web responsive con HTML, Tailwind CSS y JavaScript.
- Contenerización completa con Docker Compose.
- HTTPS automático mediante Caddy.
- Pruebas automáticas con GitHub Actions.

## Arquitectura

```mermaid
flowchart LR
    Usuario --> Cloudflare
    Cloudflare -->|HTTPS| Caddy
    Caddy --> Frontend
    Frontend -->|/api| FastAPI
    FastAPI --> PostgreSQL
    FastAPI --> Redis
    Redis --> Worker[Celery Worker]
    Redis --> Beat[Celery Beat]
    Worker --> PostgreSQL
    Worker --> Playwright
    Worker --> SendGrid
```

En producción, todos los componentes se ejecutan dentro de una instancia Amazon EC2:

- **Caddy** recibe conexiones HTTP y HTTPS.
- **Nginx** sirve el frontend y reenvía `/api` hacia FastAPI.
- **FastAPI** contiene la lógica y los endpoints.
- **PostgreSQL** conserva usuarios, productos, precios y alertas.
- **Redis** administra la cola de tareas.
- **Celery Worker** ejecuta las revisiones.
- **Celery Beat** programa las tareas periódicas.

PostgreSQL, Redis y FastAPI no publican sus puertos directamente hacia Internet.

## Tecnologías

| Área | Tecnologías |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Autenticación | JWT, bcrypt |
| Base de datos | PostgreSQL |
| Migraciones | Alembic |
| Scraping | Playwright, Chromium, BeautifulSoup |
| Tareas asíncronas | Celery, Redis |
| Notificaciones | SendGrid |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Servidores web | Nginx, Caddy |
| Contenedores | Docker, Docker Compose |
| Integración continua | GitHub Actions, pytest |
| Infraestructura | Amazon EC2, Cloudflare |

## Requisitos para desarrollo

- Git.
- Docker Engine.
- Docker Compose.
- Opcionalmente Python 3.12 y un entorno virtual para ejecutar pruebas fuera de Docker.

## Configuración local

Clona el repositorio:

```bash
git clone https://github.com/nightwolf2908/PricePulse-End-to-End-Software-.git
cd PricePulse-End-to-End-Software-
```

Crea el archivo de variables:

```bash
cp .env.example .env
```

Completa los valores de `.env`:

```env
POSTGRES_USER=pricepulse_user
POSTGRES_PASSWORD=una_contrasena_segura
POSTGRES_DB=pricepulse_db

DATABASE_URL=postgresql://pricepulse_user:una_contrasena_segura@localhost:5432/pricepulse_db

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=
ALERTA_EMAIL_PRUEBA=

JWT_SECRET=un_secreto_largo_y_aleatorio

DOMAIN=localhost
FRONTEND_BIND=0.0.0.0
FRONTEND_PORT=8080
```

`.env` contiene secretos y está excluido del repositorio mediante `.gitignore`.

Construye y levanta los contenedores:

```bash
docker compose up -d --build
```

Comprueba su estado:

```bash
docker compose ps -a
```

Abre la aplicación:

```text
http://localhost:8080
```

Documentación interactiva de FastAPI:

```text
http://localhost:8000/docs
```

Comprobación de salud:

```bash
curl http://localhost:8080/api/health
```

Respuesta esperada:

```json
{
  "estado": "ok",
  "servicio": "pricepulse-api"
}
```

## Servicios de Docker

| Servicio | Responsabilidad |
|---|---|
| `frontend` | Sirve la interfaz mediante Nginx |
| `api` | Ejecuta FastAPI |
| `postgres_db` | Almacena los datos |
| `redis` | Gestiona la cola de tareas |
| `celery_worker` | Procesa las revisiones de precios |
| `celery_beat` | Programa revisiones cada cuatro horas |
| `migrate` | Ejecuta `alembic upgrade head` |
| `caddy` | Proporciona HTTPS en producción |

El servicio `migrate` debe terminar con estado `Exited (0)`. Esto indica que las migraciones se aplicaron correctamente.

Los datos de PostgreSQL se conservan en el volumen `postgres_data`.

## API

| Método | Ruta | Descripción | Autenticación |
|---|---|---|---|
| `GET` | `/health` | Comprueba el estado de la API | No |
| `POST` | `/usuarios` | Registra un usuario | No |
| `POST` | `/login` | Genera un token JWT | No |
| `GET` | `/usuarios/me` | Devuelve el usuario actual | Sí |
| `POST` | `/productos` | Extrae y registra un producto | Sí |
| `GET` | `/productos` | Lista los productos del usuario | Sí |

Los productos admitidos actualmente deben pertenecer a:

```text
https://books.toscrape.com
```

## Procesamiento en segundo plano

Celery Beat ejecuta `programar_revisiones` cada cuatro horas. Esta tarea busca los productos activos y crea una tarea `revisar_producto` para cada uno.

Cada revisión:

1. Obtiene el producto desde PostgreSQL.
2. Abre su página con Playwright.
3. Extrae nombre, imagen y precio.
4. Guarda una nueva observación en el historial.
5. Compara el precio actual con el objetivo.
6. Envía una notificación cuando corresponde.
7. Registra la alerta para evitar envíos duplicados.

Los errores temporales de Playwright, la tienda o PostgreSQL se reintentan automáticamente.

## Pruebas

Instala las dependencias de desarrollo:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Ejecuta:

```bash
pytest
```

Las pruebas actuales validan:

- Generación y comprobación de hashes bcrypt.
- Rechazo de contraseñas incorrectas.
- Registro de usuarios.
- Inicio de sesión.
- Generación de JWT.
- Acceso a una ruta protegida.
- Rechazo de solicitudes sin token.

## Integración continua

El workflow `.github/workflows/ci.yml` se ejecuta automáticamente en:

- Cada `push` a `main`.
- Cada `pull request` dirigido a `main`.

GitHub Actions:

1. Crea un entorno Ubuntu.
2. Inicia un PostgreSQL temporal.
3. Instala Python y las dependencias.
4. Aplica las migraciones de Alembic.
5. Ejecuta las pruebas con pytest.

La base utilizada por CI es temporal y se elimina al terminar cada ejecución.

## Producción

PricePulse está desplegado en una instancia Amazon EC2 con Ubuntu.

La configuración de producción utiliza:

```env
DOMAIN=abdiel2908.com
FRONTEND_BIND=127.0.0.1
FRONTEND_PORT=8080
```

El perfil de producción se levanta con:

```bash
docker compose --profile production up -d --build
```

Caddy obtiene y renueva automáticamente los certificados HTTPS. Cloudflare administra el DNS y actúa como proxy del dominio usando el modo SSL/TLS `Full (strict)`.

## Actualización manual del servidor

Mientras se implementa el despliegue automático, una nueva versión se publica así:

```bash
cd ~/PricePulse-End-to-End-Software-
git pull origin main
docker compose --profile production up -d --build
docker compose --profile production ps -a
```

Las migraciones de Alembic se ejecutan antes de iniciar la API y los workers.

## Seguridad implementada

- Contraseñas protegidas con bcrypt.
- Autenticación mediante JWT.
- Secretos almacenados en `.env`.
- `.env` excluido de Git.
- PostgreSQL y Redis sin puertos públicos.
- FastAPI limitado a la interfaz local del servidor.
- HTTPS entre los usuarios y el servidor.
- Proxy y DNS mediante Cloudflare.
- Puerto SSH restringido mediante el grupo de seguridad de AWS.

## Limitaciones del MVP

- Solo admite productos de Books to Scrape.
- No incluye gráficas del historial.
- PostgreSQL se ejecuta dentro de la misma instancia EC2.
- La instancia EC2 es un único punto de fallo.
- El despliegue a producción todavía es manual.
- Los respaldos automáticos están pendientes.
- La aplicación está orientada al aprendizaje y no a cargas elevadas.

## Estado

PricePulse se encuentra desplegado como MVP funcional. El proyecto cubre producto, base de datos, backend, scraping, tareas asíncronas, frontend, contenerización, integración continua y despliegue en la nube.