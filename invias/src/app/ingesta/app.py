from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from invias.src.app.ingesta.elastic import updateElastic
from invias.src.app.ingesta.runt import getDataRunt
from invias.src.app.ingesta.rndc import getDataRndc

@api_view(['GET'])
def updateData(request):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    # urlElastic = 'http://20.99.184.101/elastic-api/'
    urlElastic = 'http://20.150.153.184/elastic-api/'
    dateInit = "2024-08-01"
    dateEnd = "2024-08-01"
    # Llamar a la consulta del elastic
    # response['data'] = getDataElastic()
    date = '2024-07-05T04:59:48.4'
    plate = 'KDN265'
    response['data'] = updateElastic(urlElastic, dateInit, dateEnd)
    # response['runt'] = getDataRunt(plate)
    # response['rndc'] = getDataRndc(plate, date)
    return Response(response, status=status_response)