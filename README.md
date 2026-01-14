# Software de calidad 

## Descripción

Sistema para la gestión, validación y actualización de datos e imágenes provenientes de dispositivos Conteos Moviles para INVIAS. Permite sincronizar bases de datos SQL Server y PostgreSQL, almacenamiento en Azure Blob Storage y Elastic Search. Incluye interfaz web para monitoreo y validación de procesos.

---

## Estructura del proyecto

- `/invias/src/app/ingesta`: Scripts de ingesta y validación de datos e imágenes.
- `/invias/src/flask_api`: API Flask y plantillas web para monitoreo.
- `/invias/settings.py`: Configuración de base de datos y entorno.
- `/requirements.txt`: Dependencias del proyecto.

---

## Requisitos para despliegue local

- Instancia de **PostgreSQL** (12+) corriendo en el sistema, con base de datos creada llamada `invias`, contraseña: `saroa`
- **Python 3** instalado (versión > 3.8)
- **Microsoft ODBC Driver 18 for SQL Server** instalado

---

## Despliegue local Con ejecutable Waitrees

1. **Clonar el repositorio**
   ruta:
   Elige la ubicación del proyecto, por ejemplo:  
   `C:\Software_calidad` 
   
2. **Verificar permisos de ejecución** en PowerShell:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. **Crear entorno virtual** dentro del proyecto (ejemplo: `C:\Software_Calidad`):
   ```powershell
   python -m venv env
   env\Scripts\activate
   ```
4. **Instalar dependencias Python**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configurar base de datos PostgreSQL**  
   Edita el archivo `Software_Calidad\invias\settings.py` y ajusta el bloque de bases de datos (`default`) con tu usuario, contraseña y puerto (por defecto 5432). 
6. **Iniciar la aplicación** 
    Ejecuta el archivo .bat (Softeare_Calidad.bat)
   Accede a [http://127.0.0.1:5000/](http://127.0.0.1:5000/) en tu navegador.

---

## Funcionalidades principales

- Ingesta y actualización de datos desde SQL Server y PostgreSQL hacia Elastic Search.
- Validación y sincronización de imágenes entre almacenamiento local, base de datos y Azure Blob Storage.
- Limpieza y migración de datos entre dispositivos.
- Validación de calidad de datos e imágenes con reportes y logs.
- Interfaz web para monitoreo de procesos en ejecución y visualización de logs.
- Soporte para múltiples dispositivos ANPR y manejo de grandes volúmenes de datos.

---

## Endpoints para Elastic Search

### GET /ingesta/update_data

**Descripción:**  
Consulta la base de datos del RUNT y RNDC en un rango de fechas y actualiza Elastic Search.

**Parámetros:**
- `urlElastic`: URL de Elastic Search
- `dateInit`: Fecha inicial de la consulta
- `dateEnd`: Fecha final de la consulta
- `validarRunt`: Validar si existe el campo runt en la imagen

---

### GET /ingesta/update_runt/{start}/{end}

**Descripción:**  
Consulta la base de datos del RUNT y RNDC en un rango de fechas y actualiza Elastic Search.

**Parámetros:**
- `start`: Fecha inicial de la consulta
- `end`: Fecha final de la consulta

---

### GET /ingesta/clean_data/{device}

**Descripción:**  
Limpia la base de datos de Elastic Search para el dispositivo especificado.

**Parámetros:**
- `device`: Dispositivo a limpiar

---

### GET /ingesta/pasar_data/{device}

**Descripción:**  
Pasa datos de un dispositivo a otro.

**Parámetros:**
- `device`: Dispositivo origen

---

### GET /ingesta/update_img/{device}

**Descripción:**  
Actualiza las imágenes en Azure Blob Storage encontradas en la base de datos y el dispositivo local.

**Parámetros:**
- `device`: Dispositivo al que se actualizarán las imágenes

---

### GET /ingesta/validar_faltantes/{device}

**Descripción:**  
Valida faltantes entre la base de datos de Elastic Search y la base de datos de SQL Server local para el dispositivo.

**Parámetros:**
- `device`: Dispositivo a validar

---

## Monitoreo y logs

- El progreso de los procesos puede visualizarse accediendo a la ruta `/procesos` en la aplicación web.
- Los logs y reportes de validación se almacenan en archivos de texto para su posterior revisión.

---


---

## Contacto y soporte


---

## Licencia





