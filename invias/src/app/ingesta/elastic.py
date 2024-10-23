from requests.auth import HTTPBasicAuth
import json
import requests
from django.conf import settings

from invias.src.app.ingesta.runt import getDataRunt
from invias.src.app.ingesta.rndc import getDataRndc
from invias.src.app.ingesta.tpdjson import getDataJson

def updateElastic(urlElastic, dateInit, dateEnd):
    from_num = 0
    size_num = 100
    run_state = True
    
    search_after = None
    # search_after = [1727482008280, 2.0000024]

    while run_state:
        print('while:::::::::::::::::::::::::::::::')
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
            else:
                print(':::::::::::::::::::::::::::----------------------------------------------------------:::::::::::::::::::::::::::')
                print('Cantidad consultada:::::::::::::::')
                print(len(elementos['hits']['hits']))

                from_num += 1
                print('from_num while:::::::::::::::::::::::::::::::')
                print(from_num)

                num_update = 0
                for item in elementos['hits']['hits']:
                    num_update += 1
                    print('num_update:::::::::::::::::::::::::::')
                    print(num_update)

                    print('_id________')
                    print(_id)

                    _index = item["_index"]
                    _id = item["_id"]
                
                    source = item.get("_source", {})
                    payload = source.get("payload", {})
                    
                    loadDate = source["loadDate"]
                    plate = payload["plate"]

                    try:
                        # Proceso de actualización.
                        runt = getDataRunt(plate)
                        rndc = getDataRndc(plate, loadDate)

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

                        print('data_update::::::::::::')
                        print(data_update)
                        print(url_update_index)

                        data_query_update = json.dumps(data_update)
                        update_response = requests.post(
                            urlElastic + url_update_index,
                            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
                            data=data_query_update,
                            headers=headers
                        )
                        update_response_text = json.loads(update_response.text)
                        
                        print('update_response_text:_::_:')
                        print(update_response_text)
                    except Exception as e:
                        print('data_update_error:::::::::::::::::::::')
                        print(e)
                                
                last_item = elementos['hits']['hits'][-1]
                print('LAST_ITEM:::::::::::::::::::::::::::')
                search_after = last_item['sort']
                print(search_after)
                
        except Exception as e:
            print('while_error:::::::::::::::::::::::::::::::')
            print(e)