# ** Ministerio Publication - Manual**


## Requisitos para despliegue local:
- Instancia de Postgresql (12+) corriendo en el sistema
- Python 3 instalado (versión 3.7 > )
- Ambiente virtual (opcional, pero se recomienda su uso)

## Despliegue local

1. Clonar el repositorio
2. Activar el ambiente virtual
3. Instalación de dependencias Python, correr el comando ```pip install -r requirements.txt``` el cual se encargará de instalar todas las librerias necesarias para iniciar el proyecto
4. Configurar tu base de datos local en el archivo settings.py (/backend/melmac/settings.py) donde hay un apartado de las bases de datos donde tendras que hacer cambios en el elemento default incluyendo el usuario(USER), contraseña(PASSWORD) y puerto(PORT, si la bd esta corriendo en otro puerto que no sea el 5432).
5. Crear las tablas en la base de datos ```python manage.py migrate```
6. Correr el comando ```python manage.py runserver``` donde se podra verificar que el proyecto esta corriendo correctamente y estara publicado en la ruta http://localhost:8000 por defecto.