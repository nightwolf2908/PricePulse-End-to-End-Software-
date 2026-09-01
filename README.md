# 🚀 PricePulse – SaaS End-to-End de Monitoreo de Precios

## 📌 Descripción del Proyecto
**PricePulse** es un SaaS que permite a los usuarios monitorear precios de productos en tiendas online como Amazon, Mercado Libre o eBay. Los usuarios reciben notificaciones automáticas (correo o WhatsApp) cuando el precio baja, y pueden visualizar el historial de precios en gráficos interactivos.

---

## 🧩 Fases del Proyecto

### 1. Producto y Diseño (PM / UX)
- **Requerimientos MVP**: Usuario gratuito con límite de 5 productos monitoreados.
- **Modelo de Datos**: Tablas: `Usuarios`, `Productos_Monitoreados`, `Historial_Precios`, `Alertas_Enviadas`.
- **Wireframes**: Diseño en Figma de Login, Panel Principal y Formulario de nuevo producto.

### 2. Base de Datos (Data Engineer)
- **PostgreSQL**: Base de datos relacional local.
- **Migraciones con Alembic**: Control de versiones de la estructura de la base de datos.

### 3. Backend (Backend Engineer)
- **FastAPI + Python**: API RESTful.
- **Autenticación**: JWT + encriptación de contraseñas.
- **CRUD**: Endpoints para añadir, ver, editar y eliminar productos.
- **ORM**: SQLAlchemy para interacción con PostgreSQL.

### 4. Web Scraping (Data Scraping)
- **Scraper**: BeautifulSoup o Playwright para extraer precios desde URLs.
- **Anti-bloqueo**: Rotación de User-Agents para evitar bloqueos.

### 5. Tareas en Segundo Plano (Escalabilidad)
- **Redis**: Message Broker para colas de tareas.
- **Celery**: Workers para ejecutar scraping en segundo plano.
- **Cron**: Programación cada 4 horas para actualizar precios.
- **Notificaciones**: Integración con SendGrid (correo) o Twilio (WhatsApp).

### 6. Frontend (Frontend Engineer)
- **UI**: HTML + Tailwind CSS + JavaScript (React/Next.js opcional).
- **Consumo de API**: Conexión con el backend de Python.
- **Gráficos**: Chart.js para visualizar historial de precios.

### 7. DevOps (Despliegue y Operaciones)
- **Docker**: Contenerización con Dockerfile y docker-compose.yml.
- **CI/CD**: GitHub Actions para pruebas automáticas.
- **Despliegue**: Render o Railway con variables de entorno.

### 8. Mantenimiento y Métricas (Soporte / Analytics)
- **Sentry**: Monitoreo de errores en tiempo real.

---

## 🛠️ Stack Tecnológico
| Área | Tecnologías |
|------|-------------|
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Base de Datos | PostgreSQL, Redis |
| Scraping | BeautifulSoup / Playwright |
| Tareas Asíncronas | Celery |
| Frontend | HTML, Tailwind, JavaScript / React |
| DevOps | Docker, GitHub Actions, Render/Railway |
| Monitoreo | Sentry |

---