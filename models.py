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

class HistorialPrecio(Base):
    __tablename__ = 'historial_precios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey('productos_monitoreados.id'), nullable=False)
    precio = Column(Decimal if False else Numeric(10, 2), nullable=False)  # <-- Corregido aquí
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    producto = relationship("ProductoMonitoreado", back_populates="historial_precios")
