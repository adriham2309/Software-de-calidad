from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from invias.src.app.ingesta.cleanElastic import cleanElastic, cleanElasticImg, pasarDel241al242
from threading import Thread

@api_view(['GET'])
def cleanData(request, device):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    
    # QA
    # urlElastic = 'http://20.150.153.184/elastic-api/' 

    # Prod
    urlElastic = 'http://20.99.184.101/elastic-api/'
    
    date = "2024-06-30"
    # id = "729"
    
    # Llamar a la consulta del elastic
    # response['data'] = cleanElastic(urlElastic, dateInit, dateEnd)
    # Thread(target=cleanElastic, args=(urlElastic, date, puedeEliminar)).start()
    
    Thread(target=cleanElasticImg, args=(urlElastic, device)).start()

    return Response(response, status=status_response)

@api_view(['GET'])
def pasarData(request, device):
    response = {'status': True}
    status_response = status.HTTP_200_OK
    
    # QA
    # urlElastic = 'http://20.150.153.184/elastic-api/' 

    # Prod
    urlElastic = 'http://20.99.184.101/elastic-api/'
    
    Thread(target=pasarDel241al242, args=(urlElastic, device)).start()

    return Response(response, status=status_response)