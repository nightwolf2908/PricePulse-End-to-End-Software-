from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relación: Un usuario tiene muchos productos
    productos = relationship("ProductoMonitoreado", back_populates="usuario")

class ProductoMonitoreado(Base):
    __tablename__ = 'productos_monitoreados'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    url = Column(String, nullable=False)
    precio_objetivo = Column(Numeric(10, 2), nullable=False)  # <-- Corregido aquí
    nombre = Column(String, nullable=True)
    imagen_url = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="productos")
    historial_precios = relationship("HistorialPrecio", back_populates="producto")
    alertas_enviadas = relationship("AlertaEnviada",back_populates="producto",)

class HistorialPrecio(Base):
    __tablename__ = 'historial_precios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey('productos_monitoreados.id'), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    producto = relationship("ProductoMonitoreado", back_populates="historial_precios")


class AlertaEnviada(Base):
    __tablename__ = "alertas_enviadas"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    producto_id = Column(
        Integer,
        ForeignKey("productos_monitoreados.id"),
        nullable=False,
        unique=True,
    )
    precio = Column(
        Numeric(10, 2),
        nullable=False,
    )
    fecha_envio = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    producto = relationship(
        "ProductoMonitoreado",
        back_populates="alertas_enviadas",
    )