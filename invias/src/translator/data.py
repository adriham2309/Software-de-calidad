

from django.conf import settings
from datetime import datetime, timezone, timedelta
from invias.models import (
    Device,
    SiteReferenceDevice
)
from invias.src.translator.bogota_translator import pending_data
from requests.auth import HTTPBasicAuth
import requests
import pytz
import json
import time
import collections

# Reference location - ALL device
def SitePublicationDevice(id_name, specificLane, measurementSide, pointCoordinates, reference="COMPUTER_ID"):
    # id_name
    # reference
    # specificLane - laneNumber
    # specificLane - value
    # measurementSide
    # pointCoordinates - latitude
    # pointCoordinates - longitude
    
    version = 0
    data_key = [
        "specificLane", "measurementSide", "pointCoordinates", "reference"
    ]

    site_data = {
        "specificLane": specificLane,
        "measurementSide": measurementSide,
        "pointCoordinates": pointCoordinates,
        "reference": specificLane,
    }

    send_site = False

    try:
        site_device_val = SiteReferenceDevice.objects.get(device__name=id_name, state=True)
        version = site_device_val.version
        site_json = json.loads(site_device_val.json_data)
        
        update_site = False
        try:
            for key in data_key:
                if site_data[key] != site_json[key]:
                    update_site = True
                    break
        except:
            update_site = True

        if update_site:
            site_device_val.state = False
            site_device_val.save()

            json_data = json.dumps(site_data)
            site_device_new = SiteReferenceDevice()
            site_device_new.device = site_device_val.device
            site_device_new.json_data = json_data
            site_device_new.version = version + 1
            site_device_new.save()

            send_site = True
        
    except SiteReferenceDevice.DoesNotExist:
        device_val = Device()
        device_val.name = id_name
        device_val.save()

        json_data = json.dumps(site_data)
        site_device_val = SiteReferenceDevice()
        site_device_val.device = device_val
        site_device_val.json_data = json_data
        site_device_val.save()

        send_site = True

    if send_site:
        datasendServer = str(datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%Y-%m-%dT%H:%M:%S%z"))
        publicationTime = datasendServer
        
        payload = [
            {
                "_modelBaseVersion": "3",
                "roadTrafficDataMeasurementSiteTablePublication": {
                    "lang": "en",
                    "publicationTime": publicationTime,
                    "publicationCreator": {
                        "country": settings.ENV_COUNTRY_CODE,
                        "nationalIdentifier": settings.ENV_NATIONAL_IDENTIFIER
                    },
                    "headerInformation": {
                        "informationStatus": {
                            "value" : "real"
                        }
                    },
                    "_payloadPublicationExtension" : {
                        "datasendServer" : datasendServer
                    },
                    "measurementSiteTable": [
                        {
                            "_id": "1",
                            "_version": "0",
                            "measurementSite": [
                                {
                                    "_id": id_name,
                                    "_version": str(version),
                                    "measurementEquipmentReference": reference,
                                    "measurementSpecificCharacteristics": [
                                        {
                                            "index": 1,
                                            "measurementSpecificCharacteristics": {
                                                "specificMeasurementValueType": {
                                                    "value" : "individualVehicleMeasurements"
                                                },
                                                "specificLane" : [
                                                    {
                                                        "laneNumber" : specificLane['laneNumber'],
                                                        "laneUsage": {
                                                            "value" : specificLane['value']
                                                        }
                                                    }
                                                ],
                                                "measurementSide": {
                                                    "value": measurementSide
                                                }
                                            }
                                        }
                                    ],
                                    "measurementSiteLocation" : {
                                        "locationReferencingPointLocation": {
                                            "pointByCoordinates": {
                                                "pointCoordinates": {
                                                    "latitude": pointCoordinates['latitude'],
                                                    "longitude": pointCoordinates['longitude']
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]

        pending_data(settings.MEASURED_SITE_TABLE_PUBLICATION, payload)

    locationReference = {
        "targetClass": "measurementSiteTable",
        "_version": str(version),
        "_id": id_name
    }

    # locationReference = {
    #     "locationByReference": {
    #         "predefinedLocationReference": {
    #             "targetClass": "measurementSiteTable",
    #             "_version": str(version),
    #             "_id": id_name
    #         }
    #     }
    # }

    return locationReference

# Start - DAI publication
def SituationPublication():
    print('SituationPublication::::::::::::::::')
    data_query = json.dumps({
        "from": 0,
        "size": 1000,
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
                                "gte": "2024-08-30 12:00:08.382-0500",
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
        settings.ELASTIC_URL + '/elastic-api/neural.dai.output*/_search?format=json', 
        auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
        data=data_query,
        headers=headers
    )

    elementos = json.loads(obj_response.text)
    file_data_ids = { 
        "ids": []
    }
    date_name = str(datetime.now().strftime("%d%m%Y"))
    path_id = f"{settings.BASE_DIR}/invias/src/translator/data/{settings.SITUATION_PUBLICATION}-{date_name}-ids.json"
    try:
        with open(path_id, encoding=settings.ENCODING) as f:
            file_data_ids = json.load(f)
    except FileNotFoundError:
        pass

    for dai in elementos['hits']['hits']:
        id_dai = dai["_id"]
        iddai = id_dai.replace('-','')

        if id_dai not in file_data_ids['ids']:
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

            id_name = dai["_source"]["catalog"]["desc"]
            specificLane = {
                "laneNumber": "4",
                "value": "expressLane"
            }
            measurementSide = "bothWays"
            pointCoordinates = {
                "latitude": dai["_source"]["catalog"]["lng"],
                "longitude": dai["_source"]["catalog"]["lat"]
            }

            predefinedLocationReference = SitePublicationDevice(id_name, specificLane, measurementSide, pointCoordinates)
            locationReference = {
                "locationByReference": {
                    "predefinedLocationReference": predefinedLocationReference
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

            print('payload::::::::::::::::')
            print(payload)

            pending_data(settings.SITUATION_PUBLICATION, payload)
            print('dataset pending_data forend SituationPublication')
# End - DAI publication

# Start - Conteos fijos publication
def MeasuredAndElaboratedPublication():
    print('MeasuredAndElaboratedPublication::::::::::::::::')

    # Generar la fecha y hora actual
    current_date = datetime.now()

    # Generar la fecha y hora (tiempo configurado de rango) minutos antes
    # date_before = current_date - timedelta(minutes=settings.ENV_REQUEST_TIME)
    date_before = current_date - timedelta(minutes=10)

    # Formato: yyyy-MM-dd HH:mm:ss.SSSZZ -- 2024-08-30 12:00:08.382-0500
    date_format = "%Y-%m-%d %H:%M:%S.%f%z"
    formatted_current_date = current_date.strftime(date_format)[:-3] + "+0000"
    formatted_date_before = date_before.strftime(date_format)[:-3] + "+0000"

    print("Fecha actual:", formatted_current_date)
    print("Fecha 5 minutos antes:", formatted_date_before)

    data_query = json.dumps({
        "from": 0,
        "size": 1000,
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
                                "gte": formatted_date_before,
                                "lte": formatted_current_date
                                # "lte": "2025-08-30 23:31:08.382-0500"
                            }
                        }
                    },
                    {
                        "match": {
                            "catalog.auxiliar": "F"
                        }
                    }
                ]
            }
        }
    })
    
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

    obj_response = requests.post(
        settings.ELASTIC_URL + '/elastic-api/neural.plates.output*/_search?format=json', 
        auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
        data=data_query,
        headers=headers
    )

    elementos = json.loads(obj_response.text)
    file_data_ids = { 
        "ids": []
    }
    date_name = str(datetime.now().strftime("%d%m%Y"))
    path_id = f"{settings.BASE_DIR}/invias/src/translator/data/{settings.MEASURED_DATA_PUBLICATION}-{date_name}-ids.json"
    try:
        with open(path_id, encoding=settings.ENCODING) as f:
            file_data_ids = json.load(f)
    except FileNotFoundError:
        pass

    grouped_data = GroupDataDevice(elementos['hits']['hits'], file_data_ids)

    # Para omitir los nuevos ids se guardan los que ya se estan procesando.
    for result in elementos['hits']['hits']:
        id_result = result["_id"]
        if id_result not in file_data_ids['ids']:
            print('id_result:::::')
            print(id_result)
            file_data_ids['ids'].append(id_result)

    with open(path_id, "w", encoding=settings.ENCODING) as file_sent:
        json.dump(file_data_ids, file_sent)

    """ REALIZAR LOS DIFERENTES CONDICIONALES PARA EL ANÁLISIS DE LA INFORMACIÓN """
    
    for group in grouped_data:
        min_confidence = 60
        max_speed_validate = 200

        # ----- ElaboratedData ----- 
        # Velocidad Promedio
        total_speed = 0
        amount_speed = 0
        average_speed = 0

        number_vehicles = 0

        # ----- MeasureddData ----- 
        max_speed = 80
        list_max_speed = []

        without_SOAT = []
        without_RTM = []

        for data in group['data']:
            confidence = data['payload']['confidence']
            speed = data['attributes']['speed']

            # Omitir la información con baja confianza o velocidades irregulares (muy altas o el valor -1 "no pudo obtener la velocidad")
            if float(confidence) >= min_confidence and float(speed) < max_speed_validate and speed != "-1":
                    
                total_speed += float(speed)
                amount_speed += 1

                number_vehicles += 1

                if float(speed) > max_speed:
                    list_max_speed.append(data)

                if "rndc" in data:
                    if 'SoatExpired' in data['rndc']:
                        if data['rndc']['SoatExpired'] == "SOAT VENCIDO":
                            without_SOAT.append(data)

                    if 'RtmExpired' in data['rndc']:
                        if data['rndc']['RtmExpired'] == "RTM VENCIDO":
                            without_RTM.append(data)

        try:
            average_speed = total_speed / amount_speed
        except:
            pass

        # Datos generales por grupo de datos
        print(group['desc'] + ' - ' + group['runt_class'] + ' - lane_id:' + group['lane_id'] + ' - direction:' + group['direction'])

        publicationTime = str(datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%Y-%m-%dT%H:%M:%S%z"))

        data_group = group['data'][0]
        attributes = data_group['attributes']
        id_name = group['desc']
        specificLane = {
            "laneNumber": attributes['lane_id'],
            "value": "expressLane"
        }
        measurementSide = "bothWays"
        pointCoordinates = {
            "latitude": data_group["catalog"]["lng"],
            "longitude": data_group["catalog"]["lat"]
        }
        measurementSiteTableReference = SitePublicationDevice(id_name, specificLane, measurementSide, pointCoordinates)

        print('---------------------------ElaboratedData--------------------------')
        # ----- ElaboratedData -----
        # Falta terminar los métodos para este proceso 
        print('Promedio de velocidad')
        print(average_speed)

        print('Numero de vehiculos')
        print(number_vehicles)

        print('---------------------------MeasureddData--------------------------')
        # ----- MeasureddData ----- 
        print('Cantidad de vehiculos velocidad máxima')
        print(len(list_max_speed))

        if len(list_max_speed) > 0:
            MeasurePayload(publicationTime, measurementSiteTableReference, list_max_speed, 1)
            for list in list_max_speed:
                print(list['payload']['plate'])

        print('Cantidad de vehiculos sin SOAT')
        print(len(without_SOAT))

        if len(without_SOAT) > 0:
            for list in without_SOAT:
                print(list['payload']['plate'])
            MeasurePayload(publicationTime, measurementSiteTableReference, without_SOAT, 2)

        print('Cantidad de vehiculos sin RTM')
        print(len(without_RTM))

        if len(without_RTM) > 0:
            for list in without_RTM:
                print(list['payload']['plate'])
            MeasurePayload(publicationTime, measurementSiteTableReference, without_RTM, 3)
        print('---------------------------End--------------------------')

def GroupDataDevice(elementos, file_data_ids):
    """ Agrupar la información (sitio - vehiculo - carril - dirección) """
    print('GroupDataDevice')

    # Crear un diccionario para almacenar los resultados agrupados por una clave única
    result = collections.defaultdict(lambda: {
        "runt_class": None,
        "lane_id": None,
        "direction": None,
        "data": []
    })

    # Iterar sobre cada ítem en los datos
    
    for item in elementos:
        id_result = item["_id"]
        # Validación de procesamiento.
        if id_result not in file_data_ids['ids']:
            source = item['_source']
            if 'runt' in source:
                desc = source['catalog']['desc']
                runt_class = source['runt']['class']
                lane_id = source['attributes']['lane_id']
                direction = source['payload']['direction']

                # Crear una clave única basada en desc, runt_class, lane_id y direction
                key = (desc, runt_class, lane_id, direction)

                # Asignar valores al diccionario
                result[key]["desc"] = desc
                result[key]["runt_class"] = runt_class
                result[key]["lane_id"] = lane_id
                result[key]["direction"] = direction

                # Agregar los datos originales a la lista
                result[key]["data"].append(source)

    # Convertir a una lista de diccionarios
    grouped_data = list(result.values())

    return grouped_data

def ElaboratedPayload(publicationTime):
    """ Payload - En el caso de ElaboratedData """ 
    payload = [
        {
            "_modelBaseVersion": "3",
            "elaboratedDataPublication": {
                "lang": "se",
                "publicationTime": publicationTime,
                "publicationCreator": {
                    "country": settings.ENV_COUNTRY_CODE,
                    "nationalIdentifier": settings.ENV_NATIONAL_IDENTIFIER
                },
                "periodDefault": 300.0,
                "timeDefault": "2018-10-11T15:00:00+02:00",
                "headerInformation": {
                    "confidentiality": {
                        "value": "internalUse"
                    },
                    "allowedDeliveryChannel": [
                        {
                            "value": "safetyServices"
                        },
                        {
                            "value": "vms"
                        }
                    ],
                    "informationStatus": {
                        "value": "real"
                    }
                },
                "physicalQuantity": [
                    {
                        "roadTrafficDataSinglePhysicalQuantity": {

                        }
                    }
                ]
            }
        }
    ]
    pending_data(settings.ELABORATED_DATA_PUBLICATION, payload)

def MeasurePayload(publicationTime, measurementSiteTableReference, list_data, type_data):
    """ Payload - En el caso de MeasuredData """

    physicalQuantity = []
    for vehicle_data in list_data:
        basicData = BasicDataForType(type_data, publicationTime, vehicle_data)
        laneNumber = vehicle_data['attributes']['lane_id']
        # directionPurpose values:
        if vehicle_data['payload']['direction'] == '1':
            directionPurpose = "inbound"
        else:
            directionPurpose = "outbound"

        physicalQuantityItem = {
            "index": 0,
            "physicalQuantity": {
                "roadTrafficDataSinglePhysicalQuantity": {
                    "pertinentLocation": {
                        "pointLocation": {
                            "supplementaryPositionalDescription": {
                                "directionPurpose": {
                                    "value": directionPurpose
                                },
                                "carriageway": {
                                    "carriageway": {
                                        "value": "mainCarriageway"
                                    },
                                    "lane": [{
                                        "laneNumber": laneNumber
                                    }]
                                }
                            }
                        }
                    },
                    "basicData": basicData
                }
            }
        }

        physicalQuantity.append(physicalQuantityItem)

    payload = [
        {
            "_modelBaseVersion": "3",
            "roadTrafficDataMeasuredDataPublication": {
                "headerInformation": {
                    "informationStatus": {
                        "value": "real"
                    }
                },
                "lang": "en",
                "measurementSiteTableReference": [
                    measurementSiteTableReference
                ],
                "publicationCreator": {
                    "country": settings.ENV_COUNTRY_CODE,
                    "nationalIdentifier": settings.ENV_NATIONAL_IDENTIFIER
                },
                "publicationTime": publicationTime,
                "siteMeasurements": [
                    {
                        "measurementSiteReference": measurementSiteTableReference,
                        "measurementTimeDefault": {
                            "timeValue": publicationTime
                        },
                        "physicalQuantity": physicalQuantity
                    }
                ]
            }
        }
    ]
    pending_data(settings.MEASURED_DATA_PUBLICATION, payload)
    print('payload::::::::::::::::')
    print(payload)

def BasicDataForType(type_data, publicationTime, vehicle_data):
    """ 1: max speed - 2: SOAT - 3: RTM """
    # print('BasicDataFortype')

    dict_vehicle_type = {
        "MAQ. AGRICOLA":"agriculturalVehicle",
        "BUS":"bus",
        "AUTOMOVIL":"car",
        "MAQ. CONSTRUCCION O MINERA":"constructionOrMaintenanceVehicle",
        "CAMIONETA":"fourWheelDrive",
        "TRACTOCAMION":"heavyGoodsVehicleWithTrailer",
        "CAMION":"heavyVehicle",
        "MICROBUS":"minibus",
        "MOTOCICLETA":"motorcycle",
        "MOTOTRICICLO":"motorcycleWithSideCar",
        "MOTOCARRO":"threeWheeledVehicle",
    }

    vehicleType = "Other"
    if vehicle_data["runt"]["class"] in dict_vehicle_type:
        vehicleType = dict_vehicle_type[vehicle_data["runt"]["class"]]
    
    basicData = {
        "roadIndividualVehicleDataValues": {
            "measurementOrCalculationTime": publicationTime,
            "individualVehicle": {
                "vehicleRegistrationPlateIdentifier": vehicle_data['payload']['plate'],
                "vehicleCharacteristics": {
                    "vehicleyType" : [
                        {
                            "value": vehicleType
                        }
                    ]
                }
            },
            "individualVehicleDataValuesExtensionG": {
                "urlEvidenceCar": vehicle_data['payload']['img_path'],
                "urlEvidenceVehicleRegistrationPlateIdentifier": vehicle_data['payload']['img_path_plate']
            }
        },
    }

    if type_data == 1:
        basicData['roadIndividualVehicleDataValues']['speed'] = vehicle_data['attributes']['speed']
        # Valores temporales:
        basicData['roadIndividualVehicleDataValues']['individualVehicleDataValuesExtensionG']['pointMaximumSpeed'] = 80 
        basicData['roadIndividualVehicleDataValues']['individualVehicleDataValuesExtensionG']['linealMaximumSpeed'] = 80

    elif type_data == 2:
        extensionSoat = {
            "insurancePolicyExpirationDateTime": vehicle_data['rndc']['SoatExpiration'],
            "insurancePolicyStatus": vehicle_data['rndc']['SoatExpired']
        }
        basicData['roadIndividualVehicleDataValues']['individualVehicleDataValuesExtensionG']['extensionSoat'] = extensionSoat
    
    elif type_data == 3:
        extensionVehicleInspection = {
            "expirationDate": vehicle_data['rndc']['RtmExpiration'],
            "vehicleInspectionStatus": vehicle_data['rndc']['RtmExpired']
        }
        basicData['roadIndividualVehicleDataValues']['individualVehicleDataValuesExtensionG']['extensionVehicleInspection'] = extensionVehicleInspection

    return basicData
# End - Conteos fijos publication

# Otros dispositivos