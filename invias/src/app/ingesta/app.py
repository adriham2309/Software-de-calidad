from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from invias.src.app.ingesta.elastic import updateElastic
from invias.src.app.ingesta.runt import getDataRunt
from invias.src.app.ingesta.rndc import getDataRndc
from threading import Thread

@api_view(['GET'])
def updateData(request):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    
    # QA
    urlElastic = 'http://20.150.153.184/elastic-api/' 

    # Prod
    # urlElastic = 'http://20.99.184.101/elastic-api/'
    
    dateInit = "2024-08-01 00:00:00.000-0500"
    dateEnd = "2024-08-01 23:59:59.999-0500"
    
    # Llamar a la consulta del elastic
    Thread(target=updateElastic, args=(urlElastic, dateInit, dateEnd, False)).start()

    return Response(response, status=status_response)

@api_view(['GET'])
def updateRunt(request, start, end):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    
    # QA
    # urlElastic = 'http://20.150.153.184/elastic-api/' 

    # Prod
    urlElastic = 'http://20.99.184.101/elastic-api/'
    
    dateInit = start + " 00:00:00.000-0500"
    dateEnd = end + " 23:59:59.999-0500"
    print('dateInit',dateInit)
    print('dateEnd', dateEnd)
    
    # Llamar a la consulta del elastic
    Thread(target=updateElastic, args=(urlElastic, dateInit, dateEnd, True)).start()

    return Response(response, status=status_response)