from requests.auth import HTTPBasicAuth
import json
import requests
from django.conf import settings
import pyodbc
from invias.src.flask_api.utils import agregar_proceso,actualizar_progreso,procesos_en_cola,actualizar_estado_y_progreso

def validarFaltantesLocalmente(urlElastic, device, proceso_rf):
    size_num = 10000
    run_state = True
    search_after = None
    total_elements = 0

    # Configuración de conexión
    server = '(localdb)\\aplicacion'
    database = 'ANPR' + device

    try:
        # Crear conexión y cursor
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "TrustServerCertificate=yes;"
        )
        cursor = connection.cursor()
        # Actualizar Send_Server = 0 solo una vez antes del proceso
        cursor.execute("UPDATE RESULTS SET Send_Server = 0")
        connection.commit()
        actualizar_estado_y_progreso(proceso_rf,"Actualizando Registros En Estado De Envio = 0",20)
    except Exception as e:
        print("Error al conectar a la base de datos para inicializar:", e)
        return
    finally:
        if 'connection' in locals() and connection is not None:
            connection.close()

    while run_state:
        json_data = query(size_num, device)
        if search_after:
            json_data["search_after"] = search_after

        data_query = json.dumps(json_data)
        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

        obj_response = requests.post(
            urlElastic + 'neural.plates.output*/_search?format=json',
            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
            data=data_query,
            headers=headers
        )

        try:
            elementos = json.loads(obj_response.text)
            hits = elementos['hits']['hits']
            if len(hits) == 0:
                run_state = False
                print('----- Finished -----')
                actualizar_progreso(proceso_rf, 100)
                actualizar_estado_y_progreso(proceso_rf,"Sin Registros Faltantes - Finalizado",100)

            else:
                try:
                    connection = pyodbc.connect(
                        "DRIVER={ODBC Driver 18 for SQL Server};"
                        f"SERVER={server};"
                        f"DATABASE={database};"
                        "TrustServerCertificate=yes;"
                    )
                    cursor = connection.cursor()
                    actualizar_progreso(proceso_rf, 35)

                    for item in hits:
                        incidence_id = item["_source"]['attributes']['incidence_id']
                        cursor.execute("UPDATE RESULTS SET Send_Server = 6 WHERE INCIDENCEID = ?", (incidence_id,))
                        actualizar_estado_y_progreso(proceso_rf,"Actualizando Registros Que Se Encuentran Cargados",50)

                    connection.commit()
                    last_item = hits[-1]
                    search_after = last_item['sort']
                    actualizar_estado_y_progreso(proceso_rf,"Actualizando Registros Que Se Encuentran Cargados",60)

                except Exception as e:
                    print("Error al actualizar la base de datos:", e)
                finally:
                    actualizar_progreso(proceso_rf, 85)
                    if 'connection' in locals() and connection is not None:
                        connection.close()

                total_elements += len(hits)
                print(device, '=>', total_elements)

        except Exception as e:
            print('While error:::::::::::::::::::::::::::::')
            print(e)
    actualizar_estado_y_progreso(proceso_rf,"Actualizando De Registros Faltantes Finalizada",100)

    
    
def query(size_num, id):
    return {
        "from": 0,
        "size": size_num,
        "sort": [
            {
                "@timestamp": {
                    "order": "asc"
                }
            },
            "_score"
        ],
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "catalog.desc.keyword": "INV-CONTEOS_MOVILES-"+id
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "boost": 2,
                                "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
                                "gte": "2024-01-01 00:00:00.000-0500",
                                "lte": "2024-12-31 23:59:59.999-0500"
                            }
                        }
                    }
                ]
            }
        }
    }