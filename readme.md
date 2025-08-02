# Sistema de Control de Asistencias Universitario

Este es un proyecto de aplicación web simple para gestionar el control de asistencias en un entorno universitario. Permite administrar estudiantes, profesores, materias, inscripciones y registrar la asistencia diaria.

La aplicación está construida con **Python** y el microframework **Flask** para el backend, **SQLAlchemy** como ORM para interactuar con una base de datos **SQLite**, y **HTML/CSS** para el frontend.

## Características

-   **CRUD de Profesores**: Crear, leer, actualizar y eliminar (soft delete) profesores.
-   **CRUD de Estudiantes**: Crear, leer, actualizar y eliminar (soft delete) estudiantes.
-   **CRUD de Materias**: Crear, leer, actualizar y eliminar (hard delete) materias, asignándoles un profesor.
-   **Gestión de Inscripciones**: Inscribir y anular la inscripción de estudiantes en materias.
-   **Registro de Asistencia**: Interfaz para que el profesor tome asistencia diaria para una materia.
-   **Historial y Corrección**: Ver el historial de asistencias de una materia y corregir registros individuales.
-   **Tasa de Asistencia**: Calcular y mostrar el porcentaje de asistencia de un estudiante por materia.

## Estructura del Proyecto

```
proyecto_asistencia/
├── app.py                # Aplicación principal Flask (rutas y lógica)
├── database_setup.py     # Script para inicializar la base de datos y datos de prueba
├── models.py             # Definición de los modelos de la base de datos con SQLAlchemy (ORM)
├── asistencia.db         # Archivo de la base de datos SQLite (se crea automáticamente)
├── README.md             # Este archivo
└── templates/
    ├── base.html         # Plantilla HTML base
    ├── index.html        # Página principal para tomar asistencia
    └── ... (otras plantillas .html)
└── static/
    └── css/
        └── style.css     # Hoja de estilos CSS
```

## Requisitos Previos

-   **Python 3.8** o superior.
-   **pip** (el gestor de paquetes de Python).

## Instalación

Sigue estos pasos para configurar el entorno y ejecutar la aplicación en tu máquina local.

**1. Clona el Repositorio (o descarga los archivos)**

Si estás usando git, clona el repositorio. De lo contrario, asegúrate de que todos los archivos del proyecto estén en una misma carpeta.

```bash
git clone https://github.com/V-enekoder/Asistencias.git
cd proyecto_asistencia
```

**3. Instala las Dependencias**

Instala todas las librerías de Python necesarias con pip.

```bash
pip install Flask Flask-SQLAlchemy SQLAlchemy
```

## Ejecución

**1. Configura la Base de Datos**

Este paso solo necesita realizarse **una vez** o cada vez que quieras reiniciar la base de datos a su estado inicial. Este script creará las tablas y las llenará con datos de prueba.

```bash
python database_setup.py
```
Si todo va bien, verás un mensaje indicando que las tablas se crearon y los datos se insertaron. Se creará un archivo `asistencia.db` en el directorio.

**2. Inicia la Aplicación Web**

Ejecuta el servidor de desarrollo de Flask.

```bash
python app.py
```
Verás una salida similar a esta en tu terminal:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: ...
```

**3. Accede a la Aplicación**

Abre tu navegador web y navega a la siguiente URL:

[**http://127.0.0.1:5000**](http://127.0.0.1:5000)

¡Listo! Ya puedes empezar a usar el sistema de control de asistencias.

## Solución de Problemas Comunes

-   **Error `no such table: ...`**: Este error ocurre si la base de datos no se ha creado o no está actualizada. La solución es:
    1.  Detener el servidor (Ctrl+C).
    2.  Eliminar el archivo `asistencia.db`.
    3.  Volver a ejecutar `python database_setup.py`.
    4.  Iniciar de nuevo el servidor con `python app.py`.

-   **Error `NoForeignKeysError` o `Could not determine join condition...`**: Indica un problema en la definición de las `relationship` en el archivo `models.py`. Revisa que las relaciones y los `back_populates` estén correctamente configurados entre los modelos.

---
