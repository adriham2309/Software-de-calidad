import json
import requests
import pytz
import os
import django
from invias.src.app.ingesta.elastic import updateElasticQuery
from django.conf import settings
from requests.auth import HTTPBasicAuth
from datetime import datetime
from invias.src.flask_api.utils import agregar_proceso,actualizar_progreso,procesos_en_cola,actualizar_estado_y_progreso

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invias.settings')
django.setup()


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
            
def cleanElasticImg(urlElastic, id,proceso_D):
    size_num = 10000
    run = True
    search_after = None
    i = 0
    totalregistros = 0
    puedeEliminar = True
    fecha_inicio = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
    logTxt(id, 'Inicio: ' + fecha_inicio)
    dataDelete = {}
    keysIguales = {}
    print('id', id, dataDelete)
    while run:
        json_data = jsonData1(size_num, id)
        if search_after:
            json_data["search_after"] = search_after
        # return json_data
        data_query = json.dumps(json_data)
        # print(data_query)
            
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
            
            for item in elementos['hits']['hits']:
                try:
                    actualizar_estado_y_progreso(proceso_D, "Consultando Informacion De Elastic",25)
                    _id = item['_id']
                    _index = item['_index']
                    if _id in keysIguales:
                        addkeys = keysIguales[_id]
                        addkeys.append(_index)
                        keysIguales[_id] = addkeys
                    else:
                        keysIguales[_id] = [_index]
                        
                    key = item['_id']+'_'+str(item['_source']['catalog']['id'])+'_'+item['_source']['payload']['plate']+'_'+item['_source']['@timestamp']
                    dataNew = {'_id': item['_id'], '_index': item['_index'], '@timestamp': item['_source']['@timestamp'], 'catalogId': item['_source']['catalog']['id'], 'payload': item['_source']['payload'], 'loadDate': item['_source']['loadDate']}
                    if "runt" in item["_source"]:
                        dataNew["runt"] = item["_source"]["runt"]
                    if "rndc" in item["_source"]:
                        dataNew["rndc"] = item["_source"]["rndc"]
                    if "TPDCategory" in item["_source"]:
                        dataNew["TPDCategory"] = item["_source"]["TPDCategory"]
                    if key in dataDelete:
                        addData = dataDelete[key]
                        seagrega = True
                        for exist in addData:
                            if exist['_index'] == dataNew['_index'] and exist['loadDate'] == dataNew['loadDate']:
                                seagrega = False
                        if seagrega:
                            addData.append(dataNew)
                            dataDelete[key] = addData
                    else:
                        dataDelete[key] = [dataNew]
                except Exception as e:
                    print('------------------------------------------')
                    print('For error', str(e))
                    print('------------------------------------------')
            
            if elementos['hits']['hits']:
                last_item = elementos['hits']['hits'][-1]
                search_after = last_item['sort']
            else:
                run = True
# Termina el ciclo si no hay más registros

            print('Total Registros: ', totalregistros)
            
            if len(elementos['hits']['hits']) < size_num:
                actualizar_estado_y_progreso(proceso_D, "Consultando Casos De Duplicidad En elastic",30)

                run = False
                logTxt(id, 'Total Registros: ' + str(totalregistros))
                uno = 0
                dos = 0
                tres = 0
                i = 0
                x = 0
                for key, value in dataDelete.items():
                    if len(value) == 1:
                        uno += 1
                    if len(value) > 1:
                        dos += 1
                        id_del = None
                        notImg = 0
                        #registroReal=''
                        #for item in value:
                        #    notImg += 1
                        #    if 'img_path' in item['payload'] and 'img_path_plate' in item['payload'] and 'runt' in item and 'rndc' in item:
                        #       registroReal = item['_index']+'/_doc/'+item['_id']
                        #    if 'img_path' not in item['payload'] and 'img_path_plate' not in item['payload']:
                        #        id_del = item['_index']+'/_doc/'+item['_id']
                        #if notImg == len(value) and id_del:
                        #    i += 1
                        #    print(' -- Delete Not IMG:',i, id_del)
                        #   print(' -- Info:',key, registroReal)
                        #    deleteDoc(urlElastic, id_del, id, i, puedeEliminar)
                        registroReal = None
                        for item in value:
                            if 'img_path' in item['payload'] and 'img_path_plate' in item['payload'] and 'runt' in item and 'rndc' in item:
                                registroReal = item['_index']+'/_doc/'+item['_id']
                        if registroReal:
                            for item in value:
                                id_del = item['_index']+'/_doc/'+item['_id']
                                if registroReal != id_del:
                                    i += 1
                                    print(' -- Delete Not IMG:',i, id_del)
                                    deleteDoc(urlElastic, id_del, id, i, puedeEliminar)
                                    actualizar_estado_y_progreso(proceso_D, "Eliminacion De Duplicados Finalizada",100)

                        else: # si en todos los casos tiene las imagenes
                            actualizar_progreso(proceso_D, 55)
                            validate = 0
                            id_del_1 = None
                            for item in value:
                                if 'runt' not in item:
                                    validate += 1
                                    id_del_1 = item['_index']+'/_doc/'+item['_id']
                            if validate == len(value):
                                id_del_1 = None
                                for item in value:
                                    if 'rndc' not in item:
                                        id_del_1 = item['_index']+'/_doc/'+item['_id']
                            if id_del_1:
                                i += 1
                                print(' -- Delete Not runt or rndc:',i, id_del_1)
                                deleteDoc(urlElastic, id_del_1, id, i, puedeEliminar)
                                actualizar_estado_y_progreso(proceso_D, "Eliminacion De Duplicados Finalizada",100)

                            else: 
                                actualizar_progreso(proceso_D, 65)
                                x += 1
                                index_add = 0
                                doc_delete = None
                                id_del_2 = None
                                lenfor = 0
                                for item1 in value:
                                    lenfor += 1
                                    if index_add == 0:
                                        index_add = int(item1['_index'].split('-')[1].replace('.',''))
                                        doc_delete = item1['_index']+'/_doc/'+item1['_id']
                                    else:
                                        index_new = int(item1['_index'].split('-')[1].replace('.',''))
                                        if index_add > index_new:
                                            id_del_2 = doc_delete
                                            i += 1
                                        else:
                                            id_del_2 = item1['_index']+'/_doc/'+item1['_id']
                                            i += 1
                                        if len(value) > 2 and lenfor < len(value):
                                            print(' -- Delete Older 1:',i, id_del_2)
                                            deleteDoc(urlElastic, id_del_2, id, i, puedeEliminar)
                                            actualizar_progreso(proceso_D, 100)
                                print(' -- Delete Older 2:',i, id_del_2)
                                deleteDoc(urlElastic, id_del_2, id, i, puedeEliminar)
                                actualizar_estado_y_progreso(proceso_D, "Eliminacion De Duplicados Finalizada",100)

                                
                indices_unicos = set()
                for index_list in keysIguales.values():
                    for idx in index_list:
                        indices_unicos.add(idx)
                print('--------------------------------------------------------------------------------')
                print('Lista de _index encontrados:')
                for idx in sorted(indices_unicos):
                    print('-', idx)
                print('Total de índices únicos encontrados:', len(indices_unicos)) 
                fecha_fin = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
                logTxt(id, 'Finalizo: ' + fecha_fin)
                print('--------------------------------------------------------------------------------')
                print('Inicio:', fecha_inicio)
                print('Device: ', id, ' -- Delete:', i)
                print('Fin:', fecha_fin)
                print('--------------------------------------------------------------------------------')
                actualizar_estado_y_progreso(proceso_D, "Eliminacion De Duplicados Finalizada ---- Fin Del Proceso",100)

                
        except Exception as e:
            print('errorrr', str(e))
            logTxt('errorrr', str(e))
            
            
def pasarDel241al242(urlElastic, id):
    size_num = 10000
    run = True
    search_after = None
    i = 0
    totalregistros = 0
    fecha_inicio = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
    logTxt(id, 'Inicio: ' + fecha_inicio)
    while run:
        json_data = jsonData2(size_num, id)
        if search_after:
            json_data["search_after"] = search_after
        # return json_data
        data_query = json.dumps(json_data)
        # print(data_query)
            
        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

        obj_response = requests.post(
            urlElastic+'neural.plates.output*/_search?format=json',
            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
            data=data_query,
            headers=headers
        )
        try:
            elementos = json.loads(obj_response.text)
            # print('elementos', elementos)
            totalregistros += len(elementos['hits']['hits'])
            # print('Total: ', len(elementos['hits']['hits']))
            if len(elementos['hits']['hits']) == 0:
                run = False
                logTxt(id, 'Total Registros: ' + str(totalregistros))
                fecha_fin = datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
                logTxt(id, 'Finalizo: ' + fecha_fin)
                print('--------------------------------------------------------------------------------')
                print('Fin: ', id)
                print('--------------------------------------------------------------------------------')
                print('Inicio:', fecha_inicio)
                print('Fin:', fecha_fin)
                print('--------------------------------------------------------------------------------')
            else:
                for item in elementos['hits']['hits']:
                    _index = item["_index"]
                    _id = item["_id"]
                    data_update = {
                        "doc": {
                            "catalog": {
                                "lng": -75.02942,
                                "postDesc": "11",
                                "stretchDesc": "Troncal del Magdalena",
                                "stateDesc": "Tolima",
                                "stateId": 29,
                                "subStretchDesc": "4507",
                                "stretchStatesIds": "29",
                                "postId": 574,
                                "type": 2,
                                "stretchId": 127,
                                "postDistance": 565.3,
                                "auxiliar": "M",
                                "subStretchId": 190,
                                "id": 741,
                                "lat": 3.91761,
                                "desc": "INV-CONTEOS_MOVILES-242"
                            }
                        }
                    }
                    i += 1
                    url_update_index = _index + "/_update/" + _id
                    print('data_update_index:',i, url_update_index)
                    # print(data_update)
                    # if i <= 410:
                    #     updateElasticQuery(data_update, urlElastic + url_update_index)
                
                last_item = elementos['hits']['hits'][-1]
                search_after = last_item['sort']
                print('Total Registros: ', totalregistros)
                
        except Exception as e:
            print('While error:::::::::::::::::::::::::::::', e)
            logTxt('errorrr', str(e))
            
# Funcion para eliminar un doc de elastic search                   
def deleteDoc(url, doc, date, i, puedeEliminar):
    # print(' DeleteDoc:',i, doc)
    nameFile = date
    if puedeEliminar:
        nameFile = date + '_DELETE'
    if puedeEliminar:
        logTxt(nameFile, doc)
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

def jsonData1(size_num, id):
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
                            "catalog.desc.keyword": "INV-CONTEOS_MOVILES-"+id
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "boost": 2,
                                "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
                                "gte": "2024-01-01 00:00:00.000-0500",
                                "lte": "2025-12-01 23:59:59.999-0500"
                            }
                        }
                    },
                ]
            }
        },
    }
    
def jsonData2(size_num, id):
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
                            "catalog.id": id
                        }
                    },
                    {
                        "match": {
                            "payload.site.keyword": "242"
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
                    },
                ]
            }
        },
    }