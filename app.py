# app.py
import datetime
from flask import Flask, render_template, request, redirect, url_for,flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Base, Estudiante, Materia, Inscripcion, Asistencia, Profesor

app = Flask(__name__)

app.secret_key = '123'


# Conexión a la base de datos
engine = create_engine('sqlite:///asistencia.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def index():
    """Página principal que muestra la lista de materias."""
    # --- CONSULTA MODIFICADA ---
    # Unimos con Profesor para filtrar por 'is_active'
    materias = session.query(Materia).join(Profesor).filter(Profesor.is_active == True).all()
    return render_template('index.html', materias=materias)

@app.route('/materia/<int:materia_id>')
def materia_detalle(materia_id):
    """Página para tomar asistencia de una materia específica."""
    materia = session.query(Materia).filter_by(id=materia_id).one()
    
    inscripciones = session.query(Inscripcion).join(Estudiante).filter(
        Inscripcion.materia_id == materia_id,
        Estudiante.is_active == True
    ).all()
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('materia_detalle.html', materia=materia, inscripciones=inscripciones, today=today)

@app.route('/registrar_asistencia', methods=['POST'])
def registrar_asistencia():
    """Procesa el formulario de asistencia."""
    materia_id = request.form.get('materia_id')
    fecha_str = request.form.get('fecha')
    fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    # Obtener todas las inscripciones para esta materia
    inscripciones_totales = session.query(Inscripcion).filter_by(materia_id=materia_id).all()
    
    # Obtener la lista de IDs de inscripciones de los estudiantes marcados como presentes
    presentes_ids = request.form.getlist('presente') # getlist obtiene todos los valores con el mismo name
    presentes_ids = [int(id) for id in presentes_ids] # Convertir a enteros

    # Eliminar registros de asistencia previos para esta fecha y materia para evitar duplicados
    inscripciones_ids_materia = [insc.id for insc in inscripciones_totales]
    session.query(Asistencia).filter(Asistencia.inscripcion_id.in_(inscripciones_ids_materia), Asistencia.fecha == fecha).delete(synchronize_session=False)
    session.commit()

    # Registrar la asistencia para todos los estudiantes inscritos
    for inscripcion in inscripciones_totales:
        asistio = inscripcion.id in presentes_ids
        nuevo_registro = Asistencia(
            inscripcion_id=inscripcion.id,
            fecha=fecha,
            presente=asistio
        )
        session.add(nuevo_registro)
    
    session.commit()
    return redirect(url_for('ver_asistencias', materia_id=materia_id))

@app.route('/asistencias/<int:materia_id>')
def ver_asistencias(materia_id):
    """Muestra el historial de asistencias de una materia."""
    materia = session.query(Materia).filter_by(id=materia_id).one()
    asistencias = session.query(Asistencia).join(Inscripcion).filter(Inscripcion.materia_id == materia_id).all()
    return render_template('asistencias.html', materia=materia, asistencias=asistencias)


# --- CRUD DE ESTUDIANTES ---

@app.route('/estudiantes')
def lista_estudiantes():
    """Lee y muestra todos los estudiantes ACTIVOS."""
    estudiantes = session.query(Estudiante).filter_by(is_active=True).order_by(Estudiante.apellido).all()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@app.route('/estudiantes/nuevo', methods=['GET', 'POST'])
def nuevo_estudiante():
    """Crea un nuevo estudiante."""
    if request.method == 'POST':
        codigo = request.form['codigo_estudiante']
        # Verificar si el código ya existe
        existente = session.query(Estudiante).filter_by(codigo_estudiante=codigo).first()
        if existente:
            flash('El código de estudiante ya existe.', 'danger')
            return render_template('estudiante_form.html')

        nuevo = Estudiante(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            codigo_estudiante=codigo
        )
        session.add(nuevo)
        session.commit()
        flash('Estudiante añadido con éxito.', 'success')
        return redirect(url_for('lista_estudiantes'))
    
    return render_template('estudiante_form.html')

@app.route('/estudiantes/editar/<int:estudiante_id>', methods=['GET', 'POST'])
def editar_estudiante(estudiante_id):
    """Actualiza los datos de un estudiante."""
    estudiante = session.query(Estudiante).get(estudiante_id)
    if not estudiante:
        return "Estudiante no encontrado", 404

    if request.method == 'POST':
        codigo = request.form['codigo_estudiante']
        # Verificar si el nuevo código ya lo tiene otro estudiante
        existente = session.query(Estudiante).filter(Estudiante.codigo_estudiante == codigo, Estudiante.id != estudiante_id).first()
        if existente:
            flash('El código de estudiante ya está en uso por otro estudiante.', 'danger')
            return render_template('estudiante_form.html', estudiante=estudiante)
        
        estudiante.nombre = request.form['nombre']
        estudiante.apellido = request.form['apellido']
        estudiante.codigo_estudiante = request.form['codigo_estudiante']
        session.commit()
        flash('Estudiante actualizado con éxito.', 'success')
        return redirect(url_for('lista_estudiantes'))

    return render_template('estudiante_form.html', estudiante=estudiante)

@app.route('/estudiantes/eliminar/<int:estudiante_id>', methods=['POST'])
def eliminar_estudiante(estudiante_id):
    """Elimina un estudiante (Soft Delete)."""
    estudiante = session.query(Estudiante).get(estudiante_id)
    if estudiante:
        estudiante.is_active = False 
        session.commit()
        flash('Estudiante eliminado con éxito.', 'warning')
    return redirect(url_for('lista_estudiantes'))


# --- CRUD DE PROFESORES ---

@app.route('/profesores')
def lista_profesores():
    """Lee y muestra todos los profesores ACTIVOS."""
    profesores = session.query(Profesor).filter_by(is_active=True).order_by(Profesor.apellido).all()
    return render_template('profesores.html', profesores=profesores)

@app.route('/profesores/nuevo', methods=['GET', 'POST'])
def nuevo_profesor():
    """Crea un nuevo profesor."""
    if request.method == 'POST':
        nuevo = Profesor(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            especialidad=request.form['especialidad']
        )
        session.add(nuevo)
        session.commit()
        flash('Profesor añadido con éxito.', 'success')
        return redirect(url_for('lista_profesores'))
    
    return render_template('profesor_form.html')

@app.route('/profesores/editar/<int:profesor_id>', methods=['GET', 'POST'])
def editar_profesor(profesor_id):
    """Actualiza los datos de un profesor."""
    profesor = session.query(Profesor).get(profesor_id)
    if not profesor:
        return "Profesor no encontrado", 404

    if request.method == 'POST':
        profesor.nombre = request.form['nombre']
        profesor.apellido = request.form['apellido']
        profesor.especialidad = request.form['especialidad']
        session.commit()
        flash('Profesor actualizado con éxito.', 'success')
        return redirect(url_for('lista_profesores'))

    return render_template('profesor_form.html', profesor=profesor)

@app.route('/profesores/eliminar/<int:profesor_id>', methods=['POST'])
def eliminar_profesor(profesor_id):
    """Elimina un profesor (Soft Delete)."""
    profesor = session.query(Profesor).get(profesor_id)
    if profesor:
        # Validar que el profesor no tenga materias activas asignadas
        materias_asignadas = session.query(Materia).filter_by(profesor_id=profesor.id).count()
        if materias_asignadas > 0:
            flash(f'No se puede eliminar al profesor {profesor.nombre} {profesor.apellido} porque tiene {materias_asignadas} materia(s) asignada(s). Reasígnelas primero.', 'danger')
        else:
            profesor.is_active = False # Soft Delete
            session.commit()
            flash('Profesor eliminado con éxito.', 'warning')
            
    return redirect(url_for('lista_profesores'))

# --- CRUD DE MATERIAS ---

@app.route('/materias/gestion')
def lista_materias():
    """Lee y muestra todas las materias para su gestión."""
    materias = session.query(Materia).join(Profesor).filter(Profesor.is_active == True).order_by(Materia.nombre_materia).all()
    return render_template('materias_gestion.html', materias=materias)

@app.route('/materias/nuevo', methods=['GET', 'POST'])
def nueva_materia():
    """Crea una nueva materia."""
    # Necesitamos la lista de profesores activos para el formulario
    profesores = session.query(Profesor).filter_by(is_active=True).all()
    
    if request.method == 'POST':
        codigo = request.form['codigo_materia']
        existente = session.query(Materia).filter_by(codigo_materia=codigo).first()
        if existente:
            flash('El código de materia ya existe.', 'danger')
            return render_template('materia_form.html', profesores=profesores)
            
        nueva = Materia(
            nombre_materia=request.form['nombre_materia'],
            codigo_materia=codigo,
            profesor_id=request.form['profesor_id']
        )
        session.add(nueva)
        session.commit()
        flash('Materia creada con éxito.', 'success')
        return redirect(url_for('lista_materias'))

    return render_template('materia_form.html', profesores=profesores)

@app.route('/materias/editar/<int:materia_id>', methods=['GET', 'POST'])
def editar_materia(materia_id):
    """Actualiza los datos de una materia."""
    materia = session.query(Materia).get(materia_id)
    if not materia:
        return "Materia no encontrada", 404
        
    profesores = session.query(Profesor).filter_by(is_active=True).all()

    if request.method == 'POST':
        codigo = request.form['codigo_materia']
        existente = session.query(Materia).filter(Materia.codigo_materia == codigo, Materia.id != materia_id).first()
        if existente:
            flash('El código de materia ya está en uso por otra materia.', 'danger')
            return render_template('materia_form.html', materia=materia, profesores=profesores)
            
        materia.nombre_materia = request.form['nombre_materia']
        materia.codigo_materia = request.form['codigo_materia']
        materia.profesor_id = request.form['profesor_id']
        session.commit()
        flash('Materia actualizada con éxito.', 'success')
        return redirect(url_for('lista_materias'))

    return render_template('materia_form.html', materia=materia, profesores=profesores)

@app.route('/materias/eliminar/<int:materia_id>', methods=['POST'])
def eliminar_materia(materia_id):
    """Elimina una materia (Hard Delete)."""
    materia = session.query(Materia).get(materia_id)
    if materia:
        session.delete(materia) # SQLAlchemy se encargará de borrar en cascada gracias a la configuración del modelo
        session.commit()
        flash('Materia y todos sus datos asociados han sido eliminados.', 'warning')
    return redirect(url_for('lista_materias'))


# --- GESTIÓN DE INSCRIPCIONES ---

@app.route('/inscripciones')
def gestion_inscripciones():
    """Página principal para la gestión de inscripciones, muestra lista de estudiantes."""
    estudiantes = session.query(Estudiante).filter_by(is_active=True).order_by(Estudiante.apellido).all()
    return render_template('inscripciones_lista_estudiantes.html', estudiantes=estudiantes)

@app.route('/inscripciones/estudiante/<int:estudiante_id>')
def detalle_inscripcion_estudiante(estudiante_id):
    """Muestra las materias inscritas, disponibles y la tasa de asistencia."""
    estudiante = session.query(Estudiante).get(estudiante_id)
    if not estudiante:
        return "Estudiante no encontrado", 404

    # 1. Obtener las inscripciones actuales del estudiante
    inscripciones_actuales = session.query(Inscripcion).filter_by(estudiante_id=estudiante_id).options(joinedload(Inscripcion.materia)).all()
    
    # --- NUEVA LÓGICA: CALCULAR TASA DE ASISTENCIA ---
    datos_inscripciones = []
    for inscripcion in inscripciones_actuales:
        total_clases = session.query(Asistencia).filter_by(inscripcion_id=inscripcion.id).count()
        clases_presente = session.query(Asistencia).filter_by(inscripcion_id=inscripcion.id, presente=True).count()
        
        tasa = 0
        if total_clases > 0:
            tasa = (clases_presente / total_clases) * 100
        
        datos_inscripciones.append({
            'inscripcion': inscripcion,
            'detalle': f"{clases_presente} / {total_clases}",
            'tasa': f"{tasa:.1f}%"
        })

    # 2. Obtener los IDs de las materias en las que ya está inscrito
    ids_materias_inscritas = [insc.materia_id for insc in inscripciones_actuales]

    # 3. Obtener las materias disponibles (todas menos en las que ya está inscrito)
    materias_disponibles = session.query(Materia).filter(Materia.id.notin_(ids_materias_inscritas)).all()

    return render_template(
        'inscripcion_detalle.html', 
        estudiante=estudiante, 
        datos_inscripciones=datos_inscripciones, # Pasamos los nuevos datos
        materias_disponibles=materias_disponibles
    )
@app.route('/inscripciones/inscribir', methods=['POST'])
def inscribir_estudiante():
    """Procesa el formulario para inscribir un estudiante en una materia."""
    estudiante_id = request.form.get('estudiante_id')
    materia_id = request.form.get('materia_id')

    # Validar que no exista ya la inscripción
    existente = session.query(Inscripcion).filter_by(estudiante_id=estudiante_id, materia_id=materia_id).first()
    if existente:
        flash('Este estudiante ya está inscrito en esa materia.', 'danger')
    else:
        nueva_inscripcion = Inscripcion(estudiante_id=estudiante_id, materia_id=materia_id)
        session.add(nueva_inscripcion)
        session.commit()
        flash('Estudiante inscrito correctamente.', 'success')

    return redirect(url_for('detalle_inscripcion_estudiante', estudiante_id=estudiante_id))

@app.route('/inscripciones/anular/<int:inscripcion_id>', methods=['POST'])
def anular_inscripcion(inscripcion_id):
    """Elimina un registro de inscripción (y sus asistencias en cascada)."""
    inscripcion = session.query(Inscripcion).get(inscripcion_id)
    if inscripcion:
        # Guardamos el ID del estudiante para poder redirigir correctamente
        estudiante_id = inscripcion.estudiante_id
        session.delete(inscripcion)
        session.commit()
        flash('Inscripción anulada con éxito. Se ha eliminado el historial de asistencia asociado.', 'warning')
        return redirect(url_for('detalle_inscripcion_estudiante', estudiante_id=estudiante_id))
    
    flash('No se encontró la inscripción para anular.', 'danger')
    return redirect(url_for('gestion_inscripciones'))

@app.route('/asistencia/modificar/<int:asistencia_id>', methods=['POST'])
def modificar_asistencia(asistencia_id):
    """Actualiza el estado de un registro de asistencia (presente/ausente)."""
    asistencia = session.query(Asistencia).get(asistencia_id)
    if asistencia:
        # Invertir el estado actual
        asistencia.presente = not asistencia.presente
        session.commit()
        flash(f"Se actualizó la asistencia del estudiante {asistencia.inscripcion.estudiante.nombre} para la fecha {asistencia.fecha.strftime('%d-%m-%Y')}.", 'success')
        
        # Redirigir de vuelta a la página de historial de la materia
        materia_id = asistencia.inscripcion.materia_id
        return redirect(url_for('ver_asistencias', materia_id=materia_id))
        
    flash('No se encontró el registro de asistencia.', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)