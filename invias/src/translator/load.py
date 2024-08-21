from django.conf import settings
import json

def data_assign(type_publication, data):
    base_path = 'invias/src/translator/data/' + type_publication + '.json'
    print('base_path::::::::::::')
    print(base_path)
    with open(
        settings.BASE_DIR / base_path, encoding=settings.ENCODING
    ) as file_sent:
        file_data = json.load(file_sent)
        print('file_data::::::::::::')
        print(file_data)

        






    