# PricePulse

[![Pruebas de PricePulse](https://github.com/nightwolf2908/PricePulse-End-to-End-Software-/actions/workflows/ci.yml/badge.svg)](https://github.com/nightwolf2908/PricePulse-End-to-End-Software-/actions/workflows/ci.yml)

PricePulse es un MVP de monitoreo automático de precios desarrollado para aprender el proceso completo de construcción y despliegue de software.

La aplicación permite crear una cuenta, iniciar sesión y registrar productos de [Books to Scrape](https://books.toscrape.com/). Un proceso en segundo plano consulta sus precios periódicamente y envía una alerta por correo cuando alcanzan el objetivo indicado por el usuario.

**Aplicación:** [https://abdiel2908.com](https://abdiel2908.com)

## Vista de la aplicación

![Inicio de sesión de PricePulse]

![Panel de productos monitoreados]

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
- Contenerización con Docker Compose.
- Base de datos PostgreSQL administrada con Amazon RDS.
- HTTPS mediante Caddy y Cloudflare.
- Pruebas y despliegue automático con GitHub Actions.

## Arquitectura

```mermaid
flowchart LR
    Usuario --> Cloudflare
    Cloudflare -->|HTTPS| Caddy
    Caddy --> Frontend[Nginx + Frontend]
    Frontend -->|/api| FastAPI
    FastAPI --> RDS[(Amazon RDS PostgreSQL)]
    FastAPI --> Redis
    Redis --> Worker[Celery Worker]
    Redis --> Beat[Celery Beat]
    Worker --> RDS
    Worker --> Playwright
    Worker --> SendGrid
```

En producción, los servicios de la aplicación se ejecutan mediante Docker Compose dentro de una instancia Amazon EC2. La base de datos se encuentra en Amazon RDS.

- **Cloudflare** administra el dominio y funciona como proxy.
- **Caddy** recibe las conexiones HTTP y HTTPS.
- **Nginx** sirve el frontend y reenvía `/api` hacia FastAPI.
- **FastAPI** contiene los endpoints y la lógica de negocio.
- **Amazon RDS PostgreSQL** conserva usuarios, productos, precios y alertas.
- **Redis** administra la cola de tareas.
- **Celery Worker** ejecuta las revisiones de precios.
- **Celery Beat** programa las revisiones periódicas.
- **Playwright** visita la tienda y extrae la información.
- **SendGrid** envía las alertas por correo.

RDS solo acepta conexiones procedentes de EC2. Redis y FastAPI tampoco publican sus puertos directamente hacia Internet.

## Tecnologías

| Área | Tecnologías |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Autenticación | JWT, bcrypt |
| Base de datos | PostgreSQL 15 y Amazon RDS |
| Migraciones | Alembic |
| Scraping | Playwright, Chromium, BeautifulSoup |
| Tareas asíncronas | Celery, Redis |
| Notificaciones | SendGrid |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Servidores web | Nginx, Caddy |
| Contenedores | Docker, Docker Compose |
| Pruebas | pytest |
| CI/CD | GitHub Actions, AWS OIDC y Systems Manager |
| Infraestructura | Amazon EC2, Amazon RDS, IAM, SSM y Cloudflare |

## Estructura general

```text
PricePulse/
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   └── versions/
├── frontend/
│   ├── Dockerfile
│   ├── app.js
│   ├── config.js
│   ├── index.html
│   └── nginx.conf
├── tests/
├── Caddyfile
├── Dockerfile.api
├── Dockerfile.celery
├── alembic.ini
├── celery_app.py
├── database.py
├── docker-compose.yml
├── main.py
├── models.py
├── notificaciones.py
├── scraper.py
├── seguridad.py
├── tasks.py
└── README.md
```

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

# Python ejecutado directamente en la computadora
DATABASE_URL=postgresql://pricepulse_user:una_contrasena_segura@localhost:5432/pricepulse_db

# Servicios ejecutados dentro de Docker
APP_DATABASE_URL=postgresql://pricepulse_user:una_contrasena_segura@postgres_db:5432/pricepulse_db

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

El archivo `.env` contiene secretos y está excluido del repositorio mediante `.gitignore`.

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

Comprueba la API desde el frontend:

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
| `postgres_db` | PostgreSQL para desarrollo local y recuperación |
| `redis` | Gestiona la cola de tareas |
| `celery_worker` | Procesa las revisiones de precios |
| `celery_beat` | Programa revisiones cada cuatro horas |
| `migrate` | Ejecuta las migraciones de Alembic |
| `caddy` | Proporciona HTTPS en producción |

El servicio `migrate` debe terminar con estado `Exited (0)`. Esto significa que las migraciones se aplicaron correctamente.

Los datos de PostgreSQL local se conservan en el volumen `postgres_data`.

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
3. Extrae el nombre, imagen y precio.
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

Las pruebas validan:

- Generación y comprobación de hashes bcrypt.
- Rechazo de contraseñas incorrectas.
- Registro de usuarios.
- Inicio de sesión.
- Generación de tokens JWT.
- Acceso a rutas protegidas.
- Rechazo de solicitudes sin token.

## Integración continua

El workflow `.github/workflows/ci.yml` se ejecuta automáticamente:

- Con cada `push` a `main`.
- Con cada `pull request` dirigido a `main`.

GitHub Actions:

1. Crea un entorno Ubuntu temporal.
2. Inicia una base PostgreSQL para pruebas.
3. Instala Python y las dependencias.
4. Aplica las migraciones de Alembic.
5. Ejecuta las pruebas con pytest.

La base de datos utilizada por CI es temporal y se elimina al terminar cada ejecución.

## Despliegue automático en EC2

Después de que las pruebas de un `push` a `main` terminan correctamente, GitHub Actions despliega la nueva versión en EC2.

```mermaid
sequenceDiagram
    participant Dev as Desarrollador
    participant GH as GitHub Actions
    participant AWS as AWS IAM/OIDC
    participant SSM as AWS Systems Manager
    participant EC2 as Instancia EC2

    Dev->>GH: Push a main
    GH->>GH: Ejecuta migraciones y pytest
    GH->>AWS: Solicita acceso temporal con OIDC
    AWS-->>GH: Autoriza el rol de IAM
    GH->>SSM: Envía la orden de despliegue
    SSM->>EC2: Ejecuta Git y Docker Compose
    EC2-->>GH: Devuelve el resultado
    GH->>EC2: Comprueba /api/health
```

El despliegue no almacena llaves permanentes de AWS en GitHub.

GitHub Actions presenta un token OIDC y asume temporalmente un rol de IAM. Este rol tiene permiso para enviar una orden mediante AWS Systems Manager.

La instancia EC2 también tiene un rol de IAM que permite recibir y ejecutar las órdenes de SSM.

El proceso automático:

1. Descarga el último commit con `git pull --ff-only`.
2. Construye las imágenes actualizadas.
3. Actualiza los contenedores con Docker Compose.
4. Reinicia frontend y Caddy para actualizar la comunicación interna.
5. Muestra el estado de los servicios.
6. Consulta el endpoint público `/api/health`.
7. Marca el despliegue como fallido si la aplicación no responde.

![Despliegue exitoso mediante GitHub Actions]

## Infraestructura de producción

PricePulse está desplegado en una instancia Amazon EC2 con Ubuntu.

![Instancia EC2 de PricePulse]

Los siguientes componentes se ejecutan dentro de EC2:

- Caddy.
- Nginx y el frontend.
- FastAPI.
- Redis.
- Celery Worker.
- Celery Beat.
- Playwright y Chromium.

Amazon RDS ejecuta PostgreSQL como servicio administrado fuera de EC2.

![Base de datos PostgreSQL en Amazon RDS]

EC2 se comunica con RDS mediante la red privada de AWS. El grupo de seguridad de RDS permite el puerto de PostgreSQL únicamente desde el grupo de seguridad de EC2.

La conexión se configura mediante `APP_DATABASE_URL`:

```env
APP_DATABASE_URL=postgresql://USUARIO:CONTRASEÑA@ENDPOINT_RDS:5432/pricepulse_mvp?sslmode=require
```

El valor real se guarda solamente en el archivo `.env` del servidor.

## Migración de PostgreSQL local a Amazon RDS

La base de datos originalmente se ejecutaba en un contenedor de PostgreSQL dentro de EC2.

Para trasladarla a RDS:

1. Se detuvieron temporalmente la API y los workers.
2. Se creó un respaldo con `pg_dump`.
3. Se comprobó que el respaldo tuviera información.
4. Se restauró el respaldo en Amazon RDS con `pg_restore`.
5. Se ejecutaron las migraciones de Alembic.
6. Se cambió `APP_DATABASE_URL` para apuntar a RDS.
7. Se recrearon la API, Celery Worker y Celery Beat.
8. Se validaron el inicio de sesión y los datos existentes.

El contenedor PostgreSQL local puede conservarse temporalmente como mecanismo de recuperación mientras se confirma que RDS funciona correctamente.

## Dominio y HTTPS

Cloudflare administra los registros DNS del dominio y dirige el tráfico hacia la dirección pública de EC2.

![Registros DNS administrados por Cloudflare]

La ruta de una solicitud es:

```text
Usuario
   ↓
Cloudflare
   ↓
Caddy
   ↓
Nginx
   ↓
FastAPI
   ↓
Amazon RDS
```

Caddy administra HTTPS en el servidor y Cloudflare utiliza el modo SSL/TLS `Full (strict)`.

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

## Actualización manual de respaldo

Normalmente GitHub Actions realiza el despliegue. Si fuera necesario actualizar manualmente desde EC2:

```bash
cd ~/PricePulse-End-to-End-Software-
git pull --ff-only origin main
docker compose --profile production up -d --build --remove-orphans
docker compose restart frontend caddy
docker compose --profile production ps
```

Después se comprueba la aplicación:

```bash
curl --fail https://abdiel2908.com/api/health
```

Cuando Docker recrea la API, su dirección privada puede cambiar. Por eso se reinician frontend y Caddy después de actualizar los contenedores.

## Seguridad implementada

- Contraseñas protegidas con bcrypt.
- Autenticación mediante JWT.
- Secretos almacenados en `.env`.
- `.env` excluido de Git.
- RDS limitado al grupo de seguridad de EC2.
- PostgreSQL local y Redis sin puertos públicos.
- FastAPI limitado a la interfaz local del servidor.
- HTTPS entre los usuarios y el servidor.
- Proxy y DNS mediante Cloudflare.
- Puerto SSH restringido mediante el grupo de seguridad de AWS.
- Autenticación de GitHub ante AWS mediante OIDC.
- Credenciales temporales durante los despliegues.
- Ejecución remota mediante IAM y AWS Systems Manager.

## Limitaciones del MVP

- Solo admite productos de Books to Scrape.
- No incluye gráficas del historial.
- La instancia EC2 continúa siendo un único punto de fallo para la aplicación.
- Los respaldos automáticos están pendientes.
- No existe monitoreo centralizado de errores.
- La aplicación está orientada al aprendizaje y no a cargas elevadas.

## Estado

PricePulse se encuentra desplegado como un MVP funcional.

El proyecto cubre:

- Diseño de producto.
- Modelado de base de datos.
- Backend con FastAPI.
- Autenticación y seguridad básica.
- Web scraping.
- Procesamiento asíncrono.
- Notificaciones.
- Interfaz web.
- Contenerización.
- Pruebas automatizadas.
- Integración continua.
- Base de datos administrada en AWS.
- Dominio y HTTPS.
- Despliegue automático en EC2.

Ya no se encuentra activa la pagina, las bases de datos y servidores de aws no son gratis.