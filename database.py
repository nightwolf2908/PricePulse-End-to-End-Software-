from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# La misma URL que usamos en Alembic
SQLALCHEMY_DATABASE_URL = "postgresql://pulse_admin:mi_contrasena_segura2908@localhost:5432/pricepulse_mvp"

# El motor que hablará con PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# El creador de sesiones para interactuar con las tablas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta función abrirá y cerrará la base de datos de forma segura en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
