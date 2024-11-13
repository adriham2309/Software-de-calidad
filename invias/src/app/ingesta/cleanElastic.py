import json
import requests
import pytz

from django.conf import settings
from requests.auth import HTTPBasicAuth
from datetime import datetime

def cleanElastic(urlElastic, date, puedeEliminar):
    size_num = 10000
    run = True
    search_after = None
    i = 0
    totalregistros = 0
    fecha_inicio = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
    logTxt(date, 'Inicio: ' + fecha_inicio)
    while run:
        json_data = jsonData(size_num, date)
        if search_after:
            json_data["search_after"] = search_after
        # return json_data
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
            totalregistros += len(elementos['hits']['hits'])
            # print('Total: ', len(elementos['hits']['hits']))
            if len(elementos['hits']['hits']) == 0:
                run = False
                logTxt(date, 'Total Registros: ' + str(totalregistros))
                fecha_fin = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
                logTxt(date, 'Finalizo: ' + fecha_fin)
                print('--------------------------------------------------------------------------------')
                print('Fin: ', date)
                print('--------------------------------------------------------------------------------')
                print('Inicio:', fecha_inicio)
                print('Fin:', fecha_fin)
                print('--------------------------------------------------------------------------------')
            else:
                dataDelete = {}
                for item in elementos['hits']['hits']:
                    key = item['_id']+'_'+str(item['_source']['catalog']['id'])+'_'+item['_source']['payload']['plate']+'_'+item['_source']['@timestamp']
                    dataNew = {'_id': item['_id'], '_index': item['_index'], '@timestamp': item['_source']['@timestamp'], 'catalogId': item['_source']['catalog']['id'], 'payload': item['_source']['payload']}
                    if key in dataDelete:
                        addData = dataDelete[key]
                        addData.append(dataNew)
                    else:
                        dataDelete[key] = [dataNew]
                
                for key, value in dataDelete.items():
                    if len(value) > 1:
                        primeroParaEliminar = 'SI'
                        registroValido = 'NO'
                        k = 0
                        for item in value:
                            k += 1
                            doc = item['_index']+'/_doc/'+item['_id']
                            if 'img_path' not in item['payload'] and 'img_path_plate' not in item['payload']:
                                if primeroParaEliminar == 'SI' or registroValido == 'SI':
                                    primeroParaEliminar = 'NO'
                                    i += 1
                                    deleteDoc(urlElastic, doc, date, i, puedeEliminar)
                                elif k < len(value):
                                    i += 1
                                    deleteDoc(urlElastic, doc, date, i, puedeEliminar)
                            else:
                                registroValido = 'SI'
                
                last_item = elementos['hits']['hits'][-1]
                search_after = last_item['sort']
                print('Total Registros: ', totalregistros)
                
        except Exception as e:
            logTxt('errorrr', str(e))

# Funcion para eliminar un doc de elastic search                   
def deleteDoc(url, doc, date, i, puedeEliminar):
    print('delete:',i, doc)
    nameFile = date
    if puedeEliminar:
        nameFile = date + '_DELETE'
    logTxt(nameFile, doc)
    if puedeEliminar:
        try:
            response = requests.delete(
                url + doc,
                auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS)
            )
            if response.status_code == 200:
                print('-------> OK <-------')
            else:
                logTxt('delete_requests_error_code', doc)
                print('delete: FAIL ', doc)
        except Exception as e:
            logTxt('delete_requests_error', doc)
            print('delete: ERROR ', doc, e)
            # print('Error al eliminar el documento')
                    
# Funcion para crear los logs de la aplicacion
def logTxt(name, text):
    fileInfo = open(name+".txt","a+")
    fileInfo.write(text + "\n")
    fileInfo.close()
    
def jsonData(size_num, date):
    return {
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
                            "catalog.auxiliar": "M"
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "boost": 2,
                                "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
                                "gte": date + ' 00:00:00.000-0500',
                                "lte": date + ' 23:59:59.999-0500'
                            }
                        }
                    },
                ]
            }
        },
        "aggs": {
            "group_by_id": {
                "terms": {
                    "field": "_id",
                    "size": size_num
                }
            }
        }
    }