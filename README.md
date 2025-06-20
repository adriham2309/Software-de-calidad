
## Requisitos para despliegue local:
- Instancia de Postgresql (12+) corriendo en el sistema con BD creada llamada invias, password= saroa
- Python 3 instalado (versión 3.8 > )
- Microsoft OBDC Driver 18 for sql server setup


## Despliegue local

1. Clonar el repositorio
2. Verificar los permisos de ejecucion en el terminal de power shell:

- Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

3. Crear entorno virtual dentro del proyecto ejemplo: (C:\Users\Documents\calidad_del_dato1.2) y correr los siguientes comandos:
    1. python -m venv env 
    2. env/Scripts/activate

4. Instalación de dependencias Python, correr los comandos: 
    1. ```pip install -r requirements.txt``` 
    2. ```pip install pyodbc``` 
    3. ```pip install azure-storage-blob``` pip install waitress
    4. ```pip install waitress```
    5. ```pip install json5
```

5. Configurar tu base de datos postgres local en el archivo settings.py (calidad_del_dato1.2\invias\settings.py) donde hay un apartado de las bases de datos donde tendras que hacer cambios en el elemento default incluyendo el usuario(USER), contraseña(PASSWORD) y puerto(PORT, si la bd esta corriendo en otro puerto que no sea el 5432).

6. modificar ruta archivo Software_calidad, eligiendo donde quede ubicado el proyecto ejemplo:("C:\Users\adriham\Documents\Work\Desarrollo\endpoint_calidad\calidad_del_dato1.2")
6.1 guardar arcchivo y ejecutar desde el explorador 

7. buscar url (http://127.0.0.1:5000/)




###############################################################################################################################################################################################

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



