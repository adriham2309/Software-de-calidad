from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from elasticsearch import Elasticsearch
from django.conf import settings
from requests.auth import HTTPBasicAuth
import requests
import json

from invias.src.translator.load import data_assign

@api_view(['GET'])
def elastic(request):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    # try:
    if True:
        # http://20.99.184.101/elastic-api/neural.plates.output*/_search
        # es = Elasticsearch(
        #     "http://20.99.184.101/elastic-api/",
        #     http_auth=("elastic", "$")
        # )

        # print(es.info())

        # res = es.search(index="neural.plates.output-2021.12.19", query={"match_all": {}})
        # print("Got %d Hits:" % res['hits']['total']['value'])
        # for hit in res['hits']['hits']:
        #     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])


        # ------------------------------------------------------------
        # data_query = json.dumps({
        #     "from": 0,
        #     "size": 1,
        #     "sort": [
        #         {
        #             "@timestamp": {
        #                 "order": "desc"
        #             }
        #         },
        #         "_score"
        #     ],
        #     "track_total_hits": True,
        #     "query": {
        #         "bool": {
        #             "must": [
        #                 {
        #                     "range": {
        #                         "@timestamp": {
        #                             "boost": 2,
        #                             "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
        #                             "gte": "2024-08-21 12:31:08.382-0500",
        #                             "lte": "2024-08-19 12:31:08.382-0500"
        #                         }
        #                     }
        #                 },
        #                 {
        #                     "match": {
        #                         "catalog.auxiliar": "F"
        #                     }
        #                 }
        #             ]
        #         }
        #     }
        # })

        data_query = json.dumps({
            "from": 0,
            "size": 1,
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
                                    "gte": "2024-08-19 12:31:08.382-0500",
                                    "lte": "2024-08-21 12:31:08.382-0500"
                                }
                            }
                        },
                    ]
                }
            }
        })

        # data_query = json.dumps({
        #     "from": 0,
        #     "size": 20    
        # })
        
        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

        obj_response = requests.post(
            'http://20.99.184.101/elastic-api/neural.dai.output*/_search?format=json', 
            auth=HTTPBasicAuth('elastic', 'Colombia1234$'),
            data=data_query,
            headers=headers
        )

        print('obj_response:::::::::::::::::::')
        print(obj_response)
        elementos = json.loads(obj_response.text)
        print(elementos)
        # headers=cha_header,


        response['status'] = True
        response['data'] = elementos
        status_response = status.HTTP_200_OK
    # except:
    #     pass
    return Response(response, status=status_response)

# Temporal

TYPE_PUBLICATION_DICT = {
    '1': settings.MEASURED_DATA_PUBLICATION,
    '2': settings.ELABORATED_DATA_PUBLICATION,
    '3': settings.SITUATION_PUBLICATION,
    '4': settings.MEASURED_SITE_TABLE_PUBLICATION,
    '5': settings.VMS_PUBLICATION,
    '6': settings.VMS_TABLE_PUBLICATION,
}

@api_view(['POST'])
def load_data(request, option):
    response = {'status': False}
    status_response = status.HTTP_400_BAD_REQUEST

    data = request.data
    # payload = data['payload']
    type_publication = TYPE_PUBLICATION_DICT[option]

    data = {}
    data_assign(type_publication, data)

    response['status'] = True
    status_response = status.HTTP_200_OK
    return Response(response, status=status_response)