import requests
import json
from datetime import datetime

def getDataRndc(placa, fecha):
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    fechaSplit = fecha.split('T')
    fechaControlS = fechaSplit[0].split('-')
    fechaControl = fechaControlS[2]+"/"+fechaControlS[1]+"/"+fechaControlS[0]
    data_json = {
        "acceso": {
            "usuario": "viits@9994",
            "clave": "viitsinvias"
        },
        "solicitud": {
            "tipo": "1",
            "procesoid": "39"
        },
        "variables": {
            "numidcontrolador": "8002158072",
            "CodigoPuestoControl": "1007",
            "FechaControl": fechaControl,
            "HoraControl": fechaSplit[1],
            "numPlaca": placa
        },
        "documento": {
            "numIdControlador": "8002158072",
            "CodigoPuestoControl": "1007"
        }
    }
    obj_response = requests.post(
        'https://rndcws2.mintransporte.gov.co/rest/rndc',
        json=data_json,
        headers=headers
    )
    data = json.loads(obj_response.text)
    # print(data)
    dataNew = {}
    if(data['Alertas'] != ''):
        alertas = json.loads(data['Alertas'])
        informativo = json.loads(data['Informativo'])
        dataNew = transformDataRndc(alertas, informativo)
    else:
        try:
            msj = data['Mensaje'].split('\r')
            dataNew['Errors'] = msj[0]
        except Exception as e:
            dataNew['Errors'] = data['Mensaje']
    dataNew['SessionId'] = data['SesionId']
    dataNew['EntryId'] = data['IngresoId']
        
    return dataNew

def transformDataRndc(dataAlert, dataInfo):
    dataNew = {}
    for rowA in dataAlert:
        for key, value in rowA.items():
            # print(key, value)
            if(key == 'ALERTA011'):
                dataNew['SoatExpired'] = value
            if(key == 'ALERTA012'):
                dataNew['RtmExpired'] = value
            if(key == 'ALERTA015'):
                dataNew['WithoutManifest'] = value
    
    for rowI in dataInfo:
        for key, value in rowI.items():
            if(key == 'INFOR002'):
                dataNew['CombinedConfigurationCode'] = value
            if(key == 'INFOR014'):
                fecha_obj = datetime.strptime(value, "%Y/%m/%d")
                dataNew['SoatExpiration'] = fecha_obj.strftime("%Y-%m-%dT%H:%M:%S")
            if(key == 'INFOR015'):
                fecha_obj = datetime.strptime(value, "%Y/%m/%d")
                dataNew['RtmExpiration'] = fecha_obj.strftime("%Y-%m-%dT%H:%M:%S")

    return dataNew