from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone

from invias.src.stateful.push.core import SessionManager
from invias.src.stateful.push.cms import main_task_loop
from invias.src.translator.bogota_translator import pending_data, pending_to_store

from threading import Thread

from invias.models import (
    Method_Publication,
    Pending,
    Store,
)
from datetime import datetime
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
        if (timezone.now() - method_publication_val.verification_date).total_seconds() > (60*settings.ENV_REQUEST_TIME):
            print('Start service::::')
            Thread(target=run, args=(session,)).start()
        else:
            print('You must wait to start the service again::::')
    except:
        response['method'] = {
            'name': TYPE_PUBLICATION_DICT[option],
            'message': 'First time'
        }
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
    Thread(target=process_data, args=(type_publication, payload)).start()

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)

@api_view(['POST'])
def load_multi_text(request, option, start, end):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    data = request.data
    payload_or = data['payload'].copy()
    payload = data['payload'].copy()

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
        type_publication = TYPE_PUBLICATION_DICT[option]
        Thread(target=process_data, args=(type_publication, payload)).start()

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)


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