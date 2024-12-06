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

## Endpoints para Elastic Search

### GET /ingesta/update_data

**Descripción**

Se configura una fecha inicial y final para la consulta de la base de datos del RUNT y RNDC para luego actualizar la base de datos de Elastic Search.

**Parametros**

- urlElastic: Url de Elastic Search
- dateInit: Fecha inicial de la consulta
- dateEnd: Fecha final de la consulta
- validarRunt: Validar si existe el campo runt en la imagen

### GET /ingesta/update_runt/{start}/{end}

**Descripción**

Se configura una fecha inicial y final para la consulta de la base de datos del RUNT y RNDC para luego actualizar la base de datos de Elastic Search.

**Parametros**

- start: Fecha inicial de la consulta
- end: Fecha final de la consulta

### GET /ingesta/clean_data/{device}

**Descripción**

Se configura el dispositivo para limpiar la base de datos de Elastic Search.

**Parametros**

- device: Dispositivo a limpiar

### GET /ingesta/pasar_data/{device}

**Descripción**

Se configura el dispositivo {device} para pasar data a otro dispositivo {device2}.

**Parametros**

- device: Dispositivo a pasar data

### GET /ingesta/update_img/{device}

**Descripción**

Se configura el dispositivo para actualizar las imagenes en el blobstore de Azure, encontradas en la base de datos y el dispositovo local.

**Parametros**

- device: Dispositivo al que se actualizarán las imagenes

### GET /ingesta/validar_faltantes/{device}

**Descripción**

Se configura el dispositivo para validar la faltantes de la base de datos de Elastic Search vs la base de datos de SQL Server Local.

**Parametros**

- device: Dispositivo al que se validarán las faltantes
