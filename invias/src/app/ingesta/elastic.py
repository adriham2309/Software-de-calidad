from requests.auth import HTTPBasicAuth
import json
import requests
from django.conf import settings

from invias.src.app.ingesta.runt import getDataRunt
from invias.src.app.ingesta.rndc import getDataRndc
from invias.src.app.ingesta.tpdjson import getDataJson
import psycopg2

def updateElastic(urlElastic, dateInit, dateEnd, validarRunt):
    from_num = 0
    size_num = 100
    if validarRunt:
        size_num = 1000
    run_state = True
    
    search_after = None
    # search_after = [1727482008280, 2.0000024]

    while run_state:
        print(' ')
        print('::::::::::::::::::::::::::::::: while :::::::::::::::::::::::::::::::')
        print(' ')
        json_data = {
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
                                    "gte": dateInit,
                                    "lte": dateEnd
                                }
                            }
                        },
                    ]
                }
            }
        }

        if validarRunt:
            json_data["query"]["bool"]["must_not"] = {
                "exists": {
                    "field": "runtCustom"
                }
            }
        
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
                print('FiNISHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
                print(' ')
            else:
                print('----------------------------------------------------')
                # print('Cantidad consultada:', len(elementos['hits']['hits']))
                # print(len(elementos['hits']['hits']))

                from_num += 1
                # print('from_num while: ', from_num)
                # print(from_num)

                num_update = 0
                try:
                    conn = psycopg2.connect(
                        host="psql-prod-001.postgres.database.azure.com",
                        database="cco_lite",
                        user="adminazure@psql-prod-001",
                        password="UsPt7eKmGQ"
                    )
                    for item in elementos['hits']['hits']:
                        num_update += 1
                        print('----------------------------------------------------')
                        print('num_update:', ((from_num*size_num)-size_num)+num_update, '>', dateInit)
                        if validarRunt and 'runt' in item["_source"] and 'rndc' in item["_source"] and 'class' in item["_source"]["runt"]:
                            print('---> Se encontro el campo RUNT y RNDC')
                            data_update = {
                                "doc": {
                                    "runtCustom": {
                                        "class": item["_source"]["runt"]["class"]
                                    }
                                }
                            }
                            if 'load_capacity' in item["_source"]["runt"]:
                                data_update["doc"]["runtCustom"]["load_capacity"] = item["_source"]["runt"]["load_capacity"]
                            if 'axles' in item["_source"]["runt"]:
                                data_update["doc"]["runtCustom"]["axles"] = item["_source"]["runt"]["axles"]
                            if "calculated_axles" in item["_source"]["runt"]:
                                data_update["doc"]["runtCustom"]["calculated_axles"] = item["_source"]["runt"]["calculated_axles"]
                                
                            _index = item["_index"]
                            _id = item["_id"]
                            url_update_index = _index + "/_update/" + _id
                            print('data_update_index:', url_update_index, data_update)
                            updateElasticQuery(data_update, urlElastic + url_update_index)
                        else:
                            print('---> No se encontro el campo runt')
                            updateDate(item, conn, urlElastic, dateInit)
                    
                    conn.close()             
                    last_item = elementos['hits']['hits'][-1]
                    search_after = last_item['sort']
                    print(' ')
                    logTxt('last_item_'+dateInit, str(search_after))
                    print('LAST_ITEM:', search_after)
                    # print(search_after)
                except Exception as e:
                    print('psycopg2 error:::::::::::::::::::::::::::::::')
                    logTxt('error_'+dateInit, str(e))
                    print(e)
        except Exception as e:
            print('while_error:::::::::::::::::::::::::::::::')
            logTxt('error_'+dateInit, str(e))
            print(e)
            
    
def logTxt(name, text):
    fileInfo = open(name+".txt","a+")
    fileInfo.write(text + "\n")
    fileInfo.close()
    
def updateDate(item, conn, urlElastic, dateInit):
    
    _index = item["_index"]
    _id = item["_id"]

    source = item.get("_source", {})
    payload = source.get("payload", {})
    
    loadDate = source["loadDate"]
    plate = payload["plate"]

    try:
        # Proceso de actualización.
        runt = getDataRunt(plate, conn)
        print('---> runt result: ', runt)
        rndc = getDataRndc(plate, loadDate)
        print('---> rndc result: ', rndc)

        data_update = {
            "doc": {
                "rndc": rndc,
                "runtCustom": runt
            }
        }

        tpd = {}
        if 'class' in runt:
            data_update["doc"]["runt"] = {
                "class": runt["class"],
            }
            if 'load_capacity' in runt:
                data_update["doc"]["runt"]["load_capacity"] = runt["load_capacity"]
            if 'axles' in runt:
                data_update["doc"]["runt"]["axles"] = runt["axles"]
            
            if "CombinedConfigurationCode" in rndc:
                key = str(runt["class"]) + "-" + str(runt["axles"]) + "-" + str(rndc["CombinedConfigurationCode"])
            else:
                key = str(runt["class"]) + "-" + str(runt["axles"])
            key3 = runt["class"]
                
            tpd = getDataJson(key, key3)

            normal_name = ['VOLQUETA', 'CAMION', 'TRACTOCAMION']
            inviasCustomClass = tpd["invias.class"]
            if str(runt["class"]) in normal_name:
                inviasCustomClass = str(runt["class"])

            if 'TPDCategory.id' in tpd:
                data_update["doc"]["TPDCategory"] = {
                    "id": tpd["TPDCategory.id"],
                    "class": tpd["TPDCategory"]
                }
                data_update["doc"]["inviasCustom"] = {
                    "id": tpd["inviasCustom.id"],
                    "class": inviasCustomClass,
                    "categoryId": tpd["TPDCategory.id"]
                }
                data_update["doc"]["invias"] = {
                    "id": tpd["invias.id"],
                    "class": tpd["invias.class"],
                    "categoryId": tpd["TPDCategory.id"]
                }

        url_update_index = _index + "/_update/" + _id
        # logTxt('info_'+dateInit, str(((from_num*size_num)-size_num)+num_update) + " update_index: "+ url_update_index)
        print('data_update_index:', url_update_index)
        # print(data_update)
        # print(url_update_index)
        updateElasticQuery(data_update, urlElastic + url_update_index)
        # print("update_response_text")
    except Exception as e:
        print('data_update_error:::::::::::::::::::::')
        logTxt('error_'+dateInit, "Update_index: " + _index + "/_update/" + _id)
        print(e)

def updateElasticQuery(data_update, urlElastic):
    data_query_update = json.dumps(data_update)
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    update_response = requests.post(
        urlElastic,
        auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
        data=data_query_update,
        headers=headers
    )
    update_response_text = json.loads(update_response.text)
    
    print('update_response_text:', update_response_text)