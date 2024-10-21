from requests.auth import HTTPBasicAuth
import json
import requests
from django.conf import settings

from invias.src.app.ingesta.runt import getDataRunt
from invias.src.app.ingesta.rndc import getDataRndc

def updateElastic(urlElastic, dateInit, dateEnd):
    from_num = 0
    # size_num = 10000
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
                                    "gte": dateInit + " 00:00:00.000-0500",
                                    "lte": dateEnd + " 23:59:59.999-0500"
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
                from_num += 1
                print('from_num:::::::::::::::::::::::::::::::')
                print(from_num)

                for item in elementos['hits']['hits']:
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

                        if 'class' in runt:
                            data_update["doc"]["runt"] = {
                                "class": runt["class"],
                            }

                        url_update_index = _index + "/_update/" + _id

                        # print('data_update::::::::::::')
                        # print(data_update)
                        # print(url_update_index)

                        data_query_update = json.dumps(data_update)
                        update_response = requests.post(
                            urlElastic + url_update_index,
                            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
                            data=data_query_update,
                            headers=headers
                        )
                        update_response_text = json.loads(update_response.text)
                        # print('update_response_text:_::_:')
                        # print(update_response_text)
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