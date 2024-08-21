from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone as time_zone

from invias.src.stateful.push.core import SessionManager
from invias.src.stateful.push.cms import main_task_loop
from invias.src.translator.bogota_translator import pending_data, pending_to_store

from threading import Thread

from invias.models import (
    Method_Publication,
    Pending,
    Store,
)
from datetime import datetime, timezone, timedelta

from requests.auth import HTTPBasicAuth
import requests
import json
import time
import pytz

# import datetime
import logging
import logging.config
import yaml
import asyncio

"""
-- Servicio que recibe la info la formatea. 
y la deja en el archivo de pendinetes.

-- Servicio que corre por debajo.
Verifica que si hay NO enviados (Envia al SnapShot los que encuentre). 
Recorre el acrhivo de pendientes. (Cola y los envia al putdata).
Si no lo envia pasa a no enviados.
(En el transcurso de 5 minutos).

"""

TYPE_PUBLICATION_DICT = {
    '1': settings.MEASURED_DATA_PUBLICATION,
    '2': settings.ELABORATED_DATA_PUBLICATION,
    '3': settings.SITUATION_PUBLICATION,
    '4': settings.MEASURED_SITE_TABLE_PUBLICATION,
    '5': settings.VMS_PUBLICATION,
    '6': settings.VMS_TABLE_PUBLICATION,
}

# Create your views here.
@api_view(['POST'])
def start(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    print('type_publication_dict:::::::')
    print(TYPE_PUBLICATION_DICT[option])

    session = SessionManager()
    session.typepublication = TYPE_PUBLICATION_DICT[option]
    
    try:
        method_publication_val = Method_Publication.objects.get(name=TYPE_PUBLICATION_DICT[option])
        if (time_zone.now() - method_publication_val.verification_date).total_seconds() > (60*settings.ENV_REQUEST_TIME):
            print('Start service::::')
            Thread(target=dataset, args=(option,)).start()
            time.sleep(60)
            Thread(target=run, args=(session,)).start()
        else:
            print('You must wait to start the service again::::')
    except:
        response['method'] = {
            'name': TYPE_PUBLICATION_DICT[option],
            'message': 'First time'
        }
        Thread(target=dataset, args=(option,)).start()
        time.sleep(60)
        Thread(target=run, args=(session,)).start()

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)

def run(session):
    """
    Inits the creation of the translation of a publication in a given date range
    """
    config_path = 'invias/src/translator/config.yaml'
    config = yaml.safe_load(open(config_path, encoding = settings.ENCODING))
    config_log = config['log']
    logging.config.dictConfig(config_log)
    # loop = asyncio.new_event_loop()
    # loop.create_task(main_task_loop(session))
    # loop.run_forever()

    main_task_loop(session)

    # asyncio.set_event_loop(loop)
    
@api_view(['POST'])
def load(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    data = request.data
    payload = data['payload']
    type_publication = TYPE_PUBLICATION_DICT[option]
    # Thread(target=process_data, args=(type_publication, payload)).start()
    pending_data(type_publication, payload)

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)

@api_view(['POST'])
def load_multi_text(request, option, start, end):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    data = request.data
    payload = data['payload']
    type_publication = TYPE_PUBLICATION_DICT[option]
    Thread(target=process_multi_data, args=(type_publication, payload, start, end)).start()

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)

def process_multi_data(type_publication, payload, start, end):
    """ Realiza ciclo de prueba """
    print('process_multi_data ::::::::::::::::::::::::::::')
    print(type_publication)
    
    if type_publication == 'measuredDataPublication':
        measurementSiteTableReference = payload[0]['roadTrafficDataMeasuredDataPublication']['measurementSiteTableReference'][0]['_id']
        measurementSiteReference = payload[0]['roadTrafficDataMeasuredDataPublication']['siteMeasurements'][0]['measurementSiteReference']['_id']
        for i in range(start, end):
            new_payload = payload.copy()
            new_payload[0]['roadTrafficDataMeasuredDataPublication']['measurementSiteTableReference'][0]['_id'] = (
                measurementSiteTableReference + str(i)
            )
            new_payload[0]['roadTrafficDataMeasuredDataPublication']['siteMeasurements'][0]['measurementSiteReference']['_id'] = (
                measurementSiteReference + 'J' + str(i)
            )
            print('new_payload:::::::::::::')
            print(new_payload)
            pending_data(type_publication, new_payload)

    elif type_publication == 'elaboratedDataPublication':
        for i in range(start, end):
            new_payload = payload.copy()
            pending_data(type_publication, new_payload)

    elif type_publication == 'situationPublication':
        situationPublication = payload[0]['situationPublication']['situation'][0]['id']

        for i in range(start, end):
            new_payload = payload.copy()
            new_payload[0]['situationPublication']['situation'][0]['id'] = (
                situationPublication + str(i)
            )
            print('new_payload:::::::::::::')
            print(new_payload)
            pending_data(type_publication, new_payload)

    elif type_publication == 'MeasuredSiteTablePublication':
        measurementSiteTable = payload[0]['measurementSiteTablePublication']['measurementSiteTable'][0]['id']

        for i in range(start, end):
            new_payload = payload.copy()
            new_payload[0]['measurementSiteTablePublication']['measurementSiteTable'][0]['id'] = (
                measurementSiteTable + str(i)
            )
            print('new_payload:::::::::::::')
            print(new_payload)
            pending_data(type_publication, new_payload)

    elif type_publication == 'vmsPublication':
        for i in range(start, end):
            new_payload = payload.copy()
            pending_data(type_publication, new_payload)

    elif type_publication == 'vmsTablePublication':
        vmsControllerTable = payload[0]['vmsTablePublication']['vmsControllerTable'][0]['_id']
        for i in range(start, end):
            new_payload = payload.copy()
            new_payload[0]['vmsTablePublication']['vmsControllerTable'][0]['_id'] = (
                vmsControllerTable + str(i)
            )
            print('new_payload:::::::::::::')
            print(new_payload)
            pending_data(type_publication, new_payload)

def process_data(type_publication, payload):
    """ Recibe y formatea la data, se agrega a la cola """
    print('process_data ::::::::::::::::::::::::::::')
    print(type_publication)
    print(payload)
    pending_data(type_publication, payload)

@api_view(['POST'])
def state_error(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    try:
        data = request.data
        token = data['token']
        if token == settings.TOKEN_ERROR:
            type_publication = TYPE_PUBLICATION_DICT[option]
            Thread(target=update_state, args=(type_publication,)).start()

            response['status'] = True
            status_response = status.HTTP_200_OK
    except:
        pass
    return Response(response, status=status_response)

def update_state(type_publication):
    """ Actualiza el estatus a falla """
    print('update_state ::::::::::::::::::::::::::::')

    pending_values = Pending.objects.filter(
        method_publication__name=type_publication,
        status__in=[0,1]
    )

    if pending_values:
        pending_to_store(pending_values, 4)

@api_view(['GET'])
def detail_method(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    try:
        type_publication = TYPE_PUBLICATION_DICT[option]
        data = {'method': type_publication}
        
        try:
            method_publication_val = Method_Publication.objects.get(name=type_publication)
            data['last_verification_process'] = method_publication_val.verification_date
            data['last_update'] = method_publication_val.last_process
            data['amount'] = method_publication_val.amount

            pending_count = Pending.objects.filter(
                method_publication=method_publication_val,
                status=0
            ).count()

            store_count = Store.objects.filter(
                pending__method_publication=method_publication_val,
                status=0
            ).count()

            data['pending_for_send'] = pending_count
            data['snap_shot_for_send'] = store_count
        except Method_Publication.DoesNotExist:
            pass

        response['status'] = True
        response['data'] = data
        status_response = status.HTTP_200_OK
    except:
        pass
    return Response(response, status=status_response)

@api_view(['GET'])
def open_log(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    try:
        type_publication = TYPE_PUBLICATION_DICT[option]
        data = {'method': type_publication}

        try:
            with open(settings.BASE_DIR / 'invias/src/logs/translation.log', encoding=settings.ENCODING) as file:
                lines = file.read().splitlines()
                data['log'] = lines
        except:
            pass

        response['status'] = True
        response['data'] = data
        status_response = status.HTTP_200_OK
    except:
        pass
    return Response(response, status=status_response)

def dataset(option):
    while True:
        print('dataset init')
        if option == '3':
            # ARREGLAR el orden en cola.
            data_query = json.dumps({
                "from": 0,
                "size": 150,
                "sort": [
                    {
                        "@timestamp": {
                            "order": "desc"
                        }
                    },
                    "_score"
                ],
                "track_total_hits": True,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "@timestamp": {
                                        "boost": 2,
                                        "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
                                        "gte": "2024-08-20 23:31:08.382-0500",
                                        "lte": "2025-08-30 23:31:08.382-0500"
                                    }
                                }
                            },
                        ]
                    }
                }
            })
            
            headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

            obj_response = requests.post(
                'http://20.99.184.101/elastic-api/neural.dai.output*/_search?format=json', 
                auth=HTTPBasicAuth('elastic', 'Colombia1234$'),
                data=data_query,
                headers=headers
            )

            elementos = json.loads(obj_response.text)
            
            print('elementos hits')
            file_data_ids = { 
                "ids": []
            }
            path_id = f"{settings.BASE_DIR}/invias/src/translator/situation_id.json"
            try:
                with open(path_id, encoding=settings.ENCODING) as f:
                    file_data_ids = json.load(f)
            except FileNotFoundError:
                pass

            for dai in elementos['hits']['hits']:
                id_dai = dai["_id"]
                iddai = id_dai.replace('-','')

                if id_dai not in file_data_ids['ids'] and dai["_source"]["catalog"]["desc"] == "INV-DAI-208-5501":
                    print('id_dai:::::')
                    print(id_dai)
                    file_data_ids['ids'].append(id_dai)

                    with open(path_id, "w", encoding=settings.ENCODING) as file_sent:
                        json.dump(file_data_ids, file_sent)
                    time.sleep(1)

                    datasendServer = str(datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%Y-%m-%dT%H:%M:%S%z"))
                    # datasendServer = "2022-01-20T08:50:18-05:00"

                    situationRecord = []

                    penalty_type = dai["_source"]['payload']['penalty_type_id']
                    print('penalty_type')
                    print(penalty_type)
                    
                    # '10': 'AVERAGE SPEED ALTERATION' - 'VehicleObstruction' - 'situationVehicleObstruction
                    # '7': 'WRONG WAY DETECTION' - 'VehicleObstruction' - 'vehicleOnWrongCarriageway'
                    # '9': 'ILLEGAL STOP' - 'VehicleObstruction' - 'vehicleStuck',
                    # '12': 'TRAFFIC JAM' - 'AbnormalTraffic' - 'heavyTraffic'
                    # '11': 'ABANDONED OBJECT' - 'ObstructionType' - 'objectOnTheRoad'


                    # timestamp = "2024-08-20T19:34:13.953Z"
                    timestamp = dai["_source"]['@timestamp']
                    # loadDate = "2024-08-20T19:38:43.0233943Z"
                    loadDate = dai["_source"]['loadDate']

                    try:
                        try:
                            dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                        dt_obj_local = dt_obj - timedelta(hours=5)
                        timestamp = dt_obj_local.strftime("%Y-%m-%dT%H:%M:%S%z")
                    except:
                        pass

                    try:
                        try:
                            ld_obj = datetime.strptime(loadDate[:26], "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            loadDate = loadDate[:26] + "Z"
                            ld_obj = datetime.strptime(loadDate, "%Y-%m-%dT%H:%M:%S.%f")
                        ld_obj_local = ld_obj - timedelta(hours=5)
                        loadDate = ld_obj_local.strftime("%Y-%m-%dT%H:%M:%S%z")
                    except:
                        pass
                    

                    publicationTime = datasendServer

                    data_general = {
                        "_id": id_dai,
                        "_version": "1",
                        "situationRecordCreationTime": timestamp,
                        "situationRecordVersionTime": loadDate,
                        "probabilityOfOccurrence": {
                            "value": 0
                        },
                        "validity": {
                            "validityStatus": {
                                "value": "active"
                            },
                            "validityTimeSpecification": {
                                "overallStartTime": loadDate,
                                "overallEndTime": loadDate,
                                "validPeriod": [
                                    {  
                                        "startOfPeriod": loadDate,
                                        "endOfPeriod": loadDate,
                                        "recurringTimePeriodOfDay": [{
                                            "timePeriodOfDay": {
                                                    "startTimeOfPeriod": loadDate,
                                                    "endTimeOfPeriod": loadDate
                                            }
                                        }],
                                        "recurringDayWeekMonthPeriod": [{
                                            "commonInstanceOfDayWithinMonth": { 
                                                "applicableDay": [{"value": 20 }],
                                                "aplicableMonth": [{"value": 8 }]
                                            }
                                        }]
                                    }
                                ]
                            }
                        }
                    }

                    locationReference = {
                        "locationByReference": {
                            "predefinedLocationReference": {
                                "targetClass": "measurementSiteTable",
                                "_version": "1",
                                "_id": "208-5501"
                            }
                        }
                    }

                    if penalty_type in [10, 7, 9]:
                        option_enum = {
                            10: "slowVehicle",
                            7: "vehicleOnWrongCarriageway",
                            9: "vehicleStuck",
                        }
                        enum = option_enum[penalty_type]
                        data_general.update({
                            "locationReference": locationReference,
                            "vehicleObstructionType": {
                                "value": enum
                            },
                            "involvedVehicleType": {
                                "value": 1
                            }
                        })
                        situationRecord = [{
                            'situationVehicleObstruction': data_general
                        }]

                    elif penalty_type == 12:
                        data_general.update({
                            "locationReference": locationReference,
                            "abnormalTrafficType": {
                                "value": "heavyTraffic"
                            },
                            "queueLenght": 0
                        })

                        situationRecord = [{
                            'situationGeneralObstruction': data_general
                        }]

                    elif penalty_type == 11:
                        data_general.update({
                            "locationReference": locationReference,
                            "obstructionType": [
                                {
                                    "value": "objectOnTheRoad"
                                },
                            ]
                        })
                        situationRecord = [{
                            'situationAbnormalTraffic': data_general
                        }]

                    payload = [
                        {
                            "_modelBaseVersion": "3",
                            "situationPublication": {
                                "lang": "en",
                                "publicationTime": publicationTime,
                                "publicationCreator": {
                                    "country": "CO",
                                    "nationalIdentifier": "INVIA"
                                },
                                "payloadPublicationExtension": {
                                    "datasendServer": datasendServer
                                },
                                "situation": [
                                    {
                                        "id": iddai,
                                        "headerInformation": {
                                            "informationStatus": {
                                                "value": "real"
                                            }
                                        },
                                        "situationRecord": situationRecord
                                    }
                                ]
                            }
                        }
                    ]
                    
                    type_publication = TYPE_PUBLICATION_DICT[option]
                    pending_data(type_publication, payload)
                    print('dataset pending_data forend')
        
        time.sleep(60 * settings.ENV_REQUEST_TIME)