from requests.auth import HTTPBasicAuth
import json
import requests
from django.conf import settings
import pyodbc
import os.path
from invias.src.app.ingesta.updateImgAzure import updateImgAzure

def updateImgElastic(urlElastic, device, path, database):
    size_num = 10000
    run_state = True
    
    search_after = None
    total_elements = 0
    noEncontradas = 0
    while run_state:
        json_data = query(size_num, device)
        
        if search_after:
            json_data["search_after"] = search_after

        data_query = json.dumps(json_data)
        
        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

        obj_response = requests.post(
            urlElastic+'neural.plates.output*/_search?format=json',
            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
            data=data_query,
            headers=headers
        )
        
        try:
            elementos = json.loads(obj_response.text)
            if len(elementos['hits']['hits']) == 0:
                run_state = False
                logTxt(device+'_NO_ENCONTRADAS', 'Total: '+noEncontradas)
                print('----- Finished -----')
            else:
                try:
                    # Crear conexión
                    connection = conexionDBLocal(device, database)
                    cursor = connection.cursor()
                    for item in elementos['hits']['hits']:

                        # Ejecutar una consulta de prueba
                        # print('item', item)
                        incidence_id = item["_source"]['attributes']['incidence_id']
                        number_plate = item["_source"]['payload']['plate']
                        # print('incidence_id', incidence_id)
                        # print('number_plate', number_plate)
                        cursor.execute("SELECT ai.INCIDENCEID, ai.ImageSource, ai.CutImageSource FROM RESULTS r INNER JOIN ANPR_Images ai on r.INCIDENCEID = ai.INCIDENCEID WHERE r.INCIDENCEID = ? AND r.NumberPlate = ?", (incidence_id, number_plate))
                        columns = [column[0] for column in cursor.description]  
                        rows = cursor.fetchall()
                        results = [dict(zip(columns, row)) for row in rows]
                        loadImageFull = None
                        loadImagePlate = None
                        for result in results:
                            imageSource = result['ImageSource']
                            cutImageSource = result['CutImageSource']
                            if 'c:' in imageSource:
                                imageSource = imageSource.replace('c:', path)
                            elif 'C:' in imageSource:
                                imageSource = imageSource.replace('C:', path)
                            if 'c:' in cutImageSource:
                                cutImageSource = cutImageSource.replace('c:', path)
                            elif 'C:' in cutImageSource:
                                cutImageSource = cutImageSource.replace('C:', path)
                            # print('ImageSource',result['ImageSource'])
                            # print('CutImageSource',result['CutImageSource'])
                            if os.path.exists(imageSource):
                                loadImageFull = updateImgAzure(imageSource, incidence_id)
                            else:
                                noEncontradas += 1
                                logTxt(device+'_NO_ENCONTRADAS', str(result['INCIDENCEID'])+', '+imageSource)
                            if os.path.exists(cutImageSource):
                                loadImagePlate = updateImgAzure(cutImageSource, incidence_id)
                            else:
                                noEncontradas += 1
                                logTxt(device+'_NO_ENCONTRADAS', str(result['INCIDENCEID'])+', '+cutImageSource)
                                
                            if loadImageFull and loadImagePlate:
                                data_update = {
                                    "doc": {
                                        "payload": {
                                            "img_path": loadImageFull,
                                            "img_path_plate": loadImagePlate
                                        },
                                        "attributes": {
                                            "avi_file_name": loadImageFull
                                        }
                                    }
                                }
                                
                                url_update_index = item["_index"] + "/_update/" + item["_id"]
                                data_query_update = json.dumps(data_update)
                                headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
                                update_response = requests.post(
                                    urlElastic + url_update_index,
                                    auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
                                    data=data_query_update,
                                    headers=headers
                                )
                                update_response_text = json.loads(update_response.text)
                                print('update_response_text:', update_response_text)
                                
                        # print('----------------------------------------------------')
                    last_item = elementos['hits']['hits'][-1]
                    search_after = last_item['sort']
                    
                except Exception as e:
                    print("Error al conectar a la base de datos:", e)

                finally: 
                    # Cerrar la conexión
                    if 'connection' in locals() and connection is not None:
                        connection.close()

            
                total_elements += len(elementos['hits']['hits'])
                print(device,'=>', total_elements)
                    
        except Exception as e:
            print('While error:::::::::::::::::::::::::::::')
            print(e)
    
    
def query(size_num, device):
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
                            "catalog.desc": device
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
                ],
                "must_not": {
                    "exists": {
                        "field": "payload.img_path"
                    }
                }
            }
        }
    }
    

def validarImages(device, path):

    try:
        
        database = 'ANPR'+device
        connection = conexionDBLocal(device, database)
        cursor = connection.cursor()
        
        # cursor.execute("SELECT * FROM ANPR_Images")
        cursor.execute("SELECT r.INCIDENCEID, ai.ImageSource, ai.CutImageSource FROM RESULTS r INNER JOIN ANPR_Images ai on r.INCIDENCEID = ai.INCIDENCEID")
        columns = [column[0] for column in cursor.description]  
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        count = 0
        countExist = 0
        countNotExist = 0
        for result in results:
            count += 1
            imageSource = result['ImageSource']
            if 'c:' in imageSource:
                imageSource = imageSource.replace('c:', path)
            elif 'C:' in imageSource:
                imageSource = imageSource.replace('C:', path)
                
            cutImageSource = result['CutImageSource']
            if 'c:' in cutImageSource:
                cutImageSource = cutImageSource.replace('c:', path)
            elif 'C:' in cutImageSource:
                cutImageSource = cutImageSource.replace('C:', path)
            notExistImg = ''
            notExistImgCut = ''
            if not os.path.exists(imageSource):
                notExistImg = imageSource
                countNotExist += 1
                print(count, 'NOT EXIST IMG','->', imageSource)
            else:
                countExist += 1
                print(count, 'EXIST IMG','->', imageSource)
            if not os.path.exists(cutImageSource):
                notExistImgCut = cutImageSource
                countNotExist += 1
                print(count, 'NOT EXIST IMG','->', cutImageSource)
            else:
                countExist += 1
                print(count, 'EXIST IMG','->', cutImageSource)
                
            logTxt(device+'_NOT_EXIST', str(result['INCIDENCEID'])+', '+notExistImg+', '+notExistImgCut)
        
        logTxt(device+'_resumen', 'Total: '+str(count)+', Existen: '+str(countExist)+', No Existen: '+str(countNotExist))
        print(' --> FINISHED <-- ')
        
        #Subir imagenes faltantes
        if countExist > 0:
            print(' --> Inicia proceso de subir imagenes faltantes <-- ')
            urlElastic = 'http://20.99.184.101/elastic-api/'
            updateImgElastic(urlElastic, device, path, database)
        
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        
# Funcion para crear los logs de la aplicacion
def logTxt(name, text):
    fileInfo = open(name+".txt","a+")
    fileInfo.write(text + "\n")
    fileInfo.close()
    
def conexionDBLocal(device, database):
    # Configuración de conexión 
    # server = 'localhost' # Para MAC
    server = '(localdb)\\aplicacion' # Para Windows
    username = ''
    password = ''
    ### Crear conexión para MAC
    # connection = pyodbc.connect(
    #     "DRIVER={ODBC Driver 18 for SQL Server};"
    #     f"SERVER={server};"
    #     f"DATABASE={database};"
    #     f"UID={username};"
    #     f"PWD={password};"
    #     "TrustServerCertificate=yes;"
    # )
    ### Crear conexión para Windows
    connection = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "TrustServerCertificate=yes;"
    )
    print(" -- Conexión exitosa DB Local -- ")
    return connection