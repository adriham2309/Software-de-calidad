from requests.auth import HTTPBasicAuth 
import json
import requests
from django.conf import settings
import pyodbc 
import os.path
import os
from datetime import datetime, timedelta
import time
import subprocess
from .updateImg import validar_calidad






def BD_ingesta_log(cursor, device):
    # Crear base de datos si no existe
    cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ingesta') CREATE DATABASE ingesta;")
    print("⚠️ La base de datos 'ingesta' ya existe. No se creó nuevamente (o fue creada).")

    # Crear tabla Procesos si no existe
    tabla_sql = """
    IF NOT EXISTS (
        SELECT * FROM ingesta.INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'Procesos' AND TABLE_SCHEMA = 'dbo'
    )
    BEGIN
        EXEC('
            CREATE TABLE ingesta.dbo.Procesos (
                Id_proceso INT NOT NULL IDENTITY(1,1),
                Dispositivo VARCHAR(255) NOT NULL,
                Estado INT,
                Fecha_inicio DATETIME NULL,
                Fecha_final DATETIME NULL
            )
        ')
    END
    """
    cursor.execute(tabla_sql)
    print("✅ Tabla 'Procesos' verificada o creada.")

    # Insertar nuevo registro de proceso
    fecha_inicio = datetime.now()
    insert_sql = """
    INSERT INTO ingesta.dbo.Procesos (Dispositivo, Estado, Fecha_inicio, Fecha_final)
    VALUES (?, ?, ?, NULL);
    """
    cursor.execute(insert_sql, (device, 1, fecha_inicio))
    print("✅ Registro inicial insertado en 'Procesos'.")





def restaurar(device,path, entorno_kafka):
    
    path_incidence = path
    nombre_db = f"ANPR{device}"
    sql_connection_string = f"Server=(localdb)\\aplicacion;Database={nombre_db};User Id=;Password=;MultipleActiveResultSets=true;trustServerCertificate=true;"
    device_name = device
    urlhost = 'http://0.0.0.0:8000'
    entorno_kafka1 = entorno_kafka
    server = '(localdb)\\aplicacion'

    try:
        # Crear ruta para .mdf/.ldf si no existe
        ruta_segura = r"C:\SQLData"
        os.makedirs(ruta_segura, exist_ok=True)

        # 1. Conexión a master
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server};"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 2. Registrar en bitácora (base ingesta)
        BD_ingesta_log(cursor, device)

        # 3. Verificar existencia y estado de la base de datos
        cursor.execute(f"SELECT state_desc FROM sys.databases WHERE name = '{nombre_db}';")
        row = cursor.fetchone()

        if not row:
            print(f"⛔ La base {nombre_db} no existe. Debes restaurarla manualmente primero.")
            return

        estado = row[0]
        print(f"🔍 Estado actual de la base {nombre_db}: {estado}")

        if estado != 'ONLINE':
            print(f"⛔ La base {nombre_db} está en estado '{estado}'. Espera a que esté ONLINE antes de continuar.")
            return

        # 4. Avanzar con los procesos posteriores

        # Conexión a la base restaurada
        conn2 = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={nombre_db};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        conn2.autocommit = True
        cursor2 = conn2.cursor()

        # Crear o reemplazar vista NeuralEventsView
        # 1. Eliminar vista si existe
        drop_vista_sql = "IF OBJECT_ID('dbo.NeuralEventsView', 'V') IS NOT NULL DROP VIEW dbo.NeuralEventsView;"
        cursor2.execute(drop_vista_sql)

        # 2. Crear vista (esto debe ir solo en un batch)
        create_vista_sql = """
        CREATE VIEW dbo.NeuralEventsView AS
        SELECT TOP (50)
            R.ID AS ResultId, R.INCIDENCEID, R.TimeStamp, R.computerID, R.NumberPlate, R.Send_Server, R.Date_Send_Server,
            R.IdLane, R.AverageCharacterHeigth, R.Result_Left, R.Result_Top, R.ProcessingTime,
            R.PlateFormat, R.Analytic_Type, R.DIRECTION_VECTOR, R.GlobalConfidence, R.OriginalNumberPlate,
            R.VehicleClass, R.VehicleColor, R.VehicleMake, R.VehicleType, R.RedLightPosTime,
            R.RedLightState, R.Angle, R.CharConfidence, R.nFrame, CAST(R.Speed AS decimal) AS Speed,
            A.ID AS AnprImagesId, A.ImageSource, A.CutImageSource,
            cl.ID_lane, cl.name, cl.lPoint00X, cl.lPoint00Y, cl.lPoint01X, cl.lPoint01Y,
            cl.lPoint10X, cl.lPoint10Y, cl.lPoint11X, cl.lPoint11Y, cl.name AS CameraName,
            lo.GPSLatitude, lo.GPSLongitude
        FROM dbo.RESULTS AS R
        LEFT OUTER JOIN dbo.ANPR_Images AS A
            ON R.computerID = A.computerID AND R.INCIDENCEID = A.INCIDENCEID
        LEFT OUTER JOIN dbo.CAMERA_LANE AS cl
            ON R.IdLane = cl.ID_lane
        LEFT OUTER JOIN dbo.Locations AS lo
            ON R.computerID = lo.ComputerID
        WHERE R.Send_Server = 0
        ORDER BY R.INCIDENCEID DESC;
        """
        cursor2.execute(create_vista_sql)


        # Estado 3
        cursor.execute("UPDATE ingesta.dbo.Procesos SET Estado = 3 WHERE Dispositivo = ?;", (device,))
        print("✅ Estado 3: Vista creada.")

        # Actualizar registros en results
        cursor2.execute("UPDATE dbo.RESULTS SET send_server = 0;")
        cursor.execute("UPDATE ingesta.dbo.Procesos SET Estado = 4 WHERE Dispositivo = ?;", (device,))
        print("✅ Estado 4: Registros actualizados.")

        cursor2.close()
        conn2.close()

        # Configurar appsettings
        act_appsettings(entorno_kafka1, path_incidence, sql_connection_string, device_name, urlhost)
        cursor.execute("UPDATE ingesta.dbo.Procesos SET Estado = 5 WHERE Dispositivo = ?;", (device,))
        print("✅ Estado 5: Configuración finalizada.")

        # Confirmar estado final y ejecutar hoja de vida
        cursor.execute("SELECT Estado FROM ingesta.dbo.Procesos WHERE Dispositivo = ? AND Estado = 5;", (device,))
        existe = cursor.fetchone()

        if existe:
            print('--> Inicia proceso Hoja de vida <--')
            validar_calidad(device, path)
        else:
            print("⚠️ No se completó alguno de los procesos de restauración.")

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Error en proceso de base de datos:", e)
        
        
        
#funcion para remmplazar y actualizar el archivo appsettings para ejecucion

def act_appsettings(entorno_kafka1, path_incidence, sql_connection_string, device_name, urlhost):
    json_file_path = "C:\\Ingesta_Invias_V-Prod_1.2\\appsettings.json"
    
    print("🟡 Ejecutando act_appsettings con:", entorno_kafka1, path_incidence, sql_connection_string, device_name, urlhost)


    kafka_credentials = {
        "QA": {
            "Broker": "kafka-qa.seguritech.co:9090",
            "Password": "e9a0ed9d35ea3167dc69b754e56d796ea76f7544d01eb7eff4d089246f5a6884"
        },
        "PROD": {
            "Broker": "kafka-prod.seguritech.co:9090",
            "Password": "1e862b18ad0a08e97accd8a5e1b8a1a48908427f36fb4932568657c546b4f70d"
        }
    }

    try:
        if not os.path.exists(json_file_path):
            print("❌ El archivo JSON no existe.")
            return

        # Quitar solo lectura (solo en Windows)
        if os.name == 'nt':
            os.chmod(json_file_path, 0o666)

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Asegurar estructuras clave
        data.setdefault("AppConfiguration", {})
        data.setdefault("EventRelayWorker", {})
        data["EventRelayWorker"].setdefault("KafkaConfiguration", {})
        data.setdefault("DevCatWebApiClientConfiguration", {})

        # ✅ Actualizar PathIncidence
        data["AppConfiguration"]["PathIncidence"] = path_incidence

        # ✅ Configuración de Kafka
        if entorno_kafka1 in kafka_credentials:
            cred = kafka_credentials[entorno_kafka1]
            data["EventRelayWorker"]["KafkaConfiguration"]["Broker"] = cred["Broker"]
            data["EventRelayWorker"]["KafkaConfiguration"]["SaslPassword"] = cred["Password"]

        # ✅ Cadena de conexión SQL
        data["EventRelayWorker"]["SqlConnectionString"] = sql_connection_string

        # ✅ Nombre del dispositivo
        data["DevCatWebApiClientConfiguration"]["DeviceName"] = "INV-CONTEOS_MOVILES-"+device_name

        # ✅ URL base
        data["Urls"] = urlhost

        # ✅ Guardar archivo
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ appsettings.json actualizado correctamente.")

    except json.JSONDecodeError as e:
        print(f"❌ Error en el formato del JSON: {e}")
    except IOError as e:
        print(f"❌ Error de lectura/escritura del archivo: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")



