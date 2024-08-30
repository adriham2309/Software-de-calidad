

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
        
    except SiteReferenceDevice.DoesNotExist:
        device_val = Device()
        device_val.name = id_name
        device_val.save()

        json_data = json.dumps(site_data)
        site_device_val = SiteReferenceDevice()
        site_device_val.device = device_val
        site_device_val.json_data = json_data
        site_device_val.save()

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

# DAI publication
def SituationPublication():
    print('SituationPublication_____::::::::::::::::')
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
        # with open(path_id, "w", encoding=settings.ENCODING) as file_sent:
        #     json.dump(file_data_ids, file_sent)
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
            print('dataset pending_data forend')

# Conteos fijos publication
def MeasuredPublication():

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
                                "gte": "2024-08-30 12:00:08.382-0500",
                                "lte": "2025-08-30 23:31:08.382-0500"
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

    for result in elementos['hits']['hits']:
        id_result = result["_id"]
        idresult = id_result.replace('-','')

        if id_result not in file_data_ids['ids']:
            print('id_result:::::')
            print(id_result)

            file_data_ids['ids'].append(id_result)

            with open(path_id, "w", encoding=settings.ENCODING) as file_sent:
                json.dump(file_data_ids, file_sent)
            time.sleep(1)

            publicationTime = str(datetime.now(pytz.timezone(settings.ENV_TIMEZONE)).strftime("%Y-%m-%dT%H:%M:%S%z"))
            
            # timestamp = "2022-04-04T09:05:00.000Z"
            timestamp = result["_source"]['@timestamp']

            try:
                try:
                    dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                dt_obj_local = dt_obj - timedelta(hours=5)
                timestamp = dt_obj_local.strftime("%Y-%m-%dT%H:%M:%S%z")
            except:
                pass

            attributes = result["_source"]['attributes']

            id_name = result["_source"]["catalog"]["desc"]
            # specificLane = {
            #     "laneNumber": "4",
            #     "value": "expressLane"
            # }
            specificLane = {
                "laneNumber": attributes['lane_id'],
                "value": "expressLane"
            }
            measurementSide = "bothWays"
            pointCoordinates = {
                "latitude": result["_source"]["catalog"]["lng"],
                "longitude": result["_source"]["catalog"]["lat"]
            }
            measurementSiteTableReference = SitePublicationDevice(id_name, specificLane, measurementSide, pointCoordinates)

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
                                "measurementSiteReference": {
                                    "_id": id_result,
                                    "_version": "0",
                                    "targetClass": "measurementSiteTable"
                                },
                                "measurementTimeDefault": {
                                    "timeValue": timestamp
                                },
                                "physicalQuantity": [
                                    {
                                        "index": 0,
                                        "physicalQuantity": {
                                            "roadTrafficDataSinglePhysicalQuantity": {
                                                "basicData": {
                                                    "measurementOrCalculationTime": {
                                                        "timePrecision": "minute"
                                                    },
                                                    "trafficData": {
                                                        "vehicleCaracteristics": {
                                                            "vehicleType": "carOrLightVehicle"
                                                        }
                                                    },
                                                    "trafficFlow": {
                                                        "vehicleFlowValue": {
                                                            "vehicleFlowRate": "16"
                                                        }
                                                    },
                                                    "trafficHeadway": {
                                                        "_averageDistanceHeadway": {
                                                            "distance": "16666"
                                                        }
                                                    },
                                                    "trafficSpeed": {
                                                        "averageVehicleSpeed": {
                                                            "speed": attributes['speed']
                                                        }
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

            print('payload::::::::::::::::')
            print(payload)

            pending_data(settings.MEASURED_DATA_PUBLICATION, payload)
            print('dataset pending_data forend')