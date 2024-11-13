from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from invias.src.app.ingesta.cleanElastic import cleanElastic 
from threading import Thread

@api_view(['GET'])
def cleanData(request):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    
    # QA
    # urlElastic = 'http://20.150.153.184/elastic-api/' 

    # Prod
    urlElastic = 'http://20.99.184.101/elastic-api/'
    
    date = "2024-06-30"
    puedeEliminar = True
    
    # Llamar a la consulta del elastic
    # response['data'] = cleanElastic(urlElastic, dateInit, dateEnd)
    Thread(target=cleanElastic, args=(urlElastic, date, puedeEliminar)).start()

    return Response(response, status=status_response)