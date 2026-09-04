import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    (
        "postgresql://pulse_admin:"
        "mi_contrasena_segura2908"
        "@localhost:5432/pricepulse_mvp"
    ),
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
