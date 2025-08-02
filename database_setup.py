# database_setup.py
import datetime
from models import Asistencia, Base, Profesor, Estudiante, Materia, Inscripcion, engine, session

# Crear todas las tablas
Base.metadata.create_all(engine)
print("Tablas creadas en la base de datos.")

# Limpiar datos existentes (opcional, útil para pruebas)
session.query(Inscripcion).delete()
session.query(Asistencia).delete()
session.query(Materia).delete()
session.query(Profesor).delete()
session.query(Estudiante).delete()
session.commit()

# --- Insertar Datos de Prueba ---

# Profesores
prof1 = Profesor(nombre="Alberto", apellido="García", especialidad="Bases de Datos")
prof2 = Profesor(nombre="Beatriz", apellido="Campos", especialidad="Desarrollo Web")

# Estudiantes
est1 = Estudiante(nombre="Carlos", apellido="Ruiz", codigo_estudiante="E2023001")
est2 = Estudiante(nombre="Diana", apellido="Solis", codigo_estudiante="E2023002")
est3 = Estudiante(nombre="Elena", apellido="Mora", codigo_estudiante="E2023003")

# Materias
mat1 = Materia(nombre_materia="Bases de Datos Avanzadas", codigo_materia="BDA-101", profesor=prof1)
mat2 = Materia(nombre_materia="Programación con Python", codigo_materia="PY-101", profesor=prof2)

session.add_all([prof1, prof2, est1, est2, est3, mat1, mat2])
session.commit() # Commit para que los IDs se generen

# Inscripciones
# Carlos y Diana en Bases de Datos
insc1 = Inscripcion(estudiante=est1, materia=mat1)
insc2 = Inscripcion(estudiante=est2, materia=mat1)
# Diana y Elena en Python
insc3 = Inscripcion(estudiante=est2, materia=mat2)
insc4 = Inscripcion(estudiante=est3, materia=mat2)

session.add_all([insc1, insc2, insc3, insc4])
session.commit()

print("Datos de prueba insertados correctamente.")
session.close()