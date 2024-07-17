from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from invias.src.stateful.push.core import SessionManager
from invias.src.stateful.push.cms import main_task_loop
from invias.src.translator.bogota_translator import pending_data

from threading import Thread

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

def process_data(type_publication, payload):
    """ Recibe y formatea la data, se agrega a la cola """
    print('process_data ::::::::::::::::::::::::::::')
    print(type_publication)
    print(payload)
    pending_data(type_publication, payload)