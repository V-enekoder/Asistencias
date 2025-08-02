# models.py
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

class Profesor(Base):
    __tablename__ = 'profesores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    especialidad = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    codigo_estudiante = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Materia(Base):
    __tablename__ = 'materias'
    id = Column(Integer, primary_key=True)
    nombre_materia = Column(String(100), nullable=False)
    codigo_materia = Column(String(20), unique=True, nullable=False)
    profesor_id = Column(Integer, ForeignKey('profesores.id'))
    profesor = relationship("Profesor")
    inscripciones = relationship("Inscripcion", back_populates="materia", cascade="all, delete-orphan")

class Inscripcion(Base):
    __tablename__ = 'inscripciones'
    id = Column(Integer, primary_key=True)
    estudiante_id = Column(Integer, ForeignKey('estudiantes.id'))
    materia_id = Column(Integer, ForeignKey('materias.id'))
    fecha_inscripcion = Column(Date, default=datetime.date.today)
    
    estudiante = relationship("Estudiante")
    materia = relationship("Materia")
    asistencias = relationship("Asistencia", back_populates="inscripcion", cascade="all, delete-orphan")

class Asistencia(Base):
    __tablename__ = 'asistencias'
    id = Column(Integer, primary_key=True)
    inscripcion_id = Column(Integer, ForeignKey('inscripciones.id'))
    fecha = Column(Date, nullable=False)
    presente = Column(Boolean, default=False, nullable=False)

    inscripcion = relationship("Inscripcion", back_populates="asistencias")

# Configuración de la base de datos
engine = create_engine('sqlite:///asistencia.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()