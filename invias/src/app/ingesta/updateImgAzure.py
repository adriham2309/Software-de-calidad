import json
import requests
from azure.storage.blob import BlobServiceClient
from requests.auth import HTTPBasicAuth
from django.conf import settings

def updateImgAzure(pathImage, incidenceid):
    try:
        parts = pathImage.split('/')
        fullName = parts[len(parts) - 1];
        
        if '#INV#' in fullName:
            fDate = fullName[0:8]
            cid = fullName.split('_')[1];
            complement = fullName.split("#INV#")[1];
        else:
            fDate = parts[len(parts) - 2];
            data = fullName.split('_')[0];
            cid = data.split('-')[1];
            complement = "." + fullName.split(".")[1];
            if '_cut' in fullName:
                complement = "_cut" + complement;
        
        fileNameBlob = "c:/tmp/imgs/" + str(fDate) + "/" + str(incidenceid) + "-" + str(cid) + str(complement);
        urlBlob = "https://repositorioneurallabs.blob.core.windows.net/imagenes/" + fileNameBlob;
        # print('-----------------------------------------------------')
        # print('fileNameBlob', fileNameBlob)
        # print('urlBlob', urlBlob)
        
        # Configuración
        sas_token = "sp=racwdli&st=2023-10-30T13:57:08Z&se=2050-11-30T21:57:08Z&spr=https&sv=2022-11-02&sr=c&sig=9OdbNXTu7IAnMiUagvP6n7PkiJu9N8ErLgjUX%2BQ%2Bv3w%3D"
        connection_string = "https://repositorioneurallabs.blob.core.windows.net"  # Cadena de conexión de tu cuenta de almacenamiento
        
        container_name = "imagenes"  # Nombre del contenedor (debe existir)
        blob_name = fileNameBlob  # Nombre con el que se guardará en el Blob Storage
        file_path = pathImage  # Ruta local al archivo
        
        # Crear cliente de servicio Blob
        blob_service_client = BlobServiceClient(connection_string, sas_token)
        
        # Crear cliente de contenedor
        container_client = blob_service_client.get_container_client(container_name)
        
        # Verificar si el contenedor existe, si no, crearlo
        # if not container_client.exists():
        #     print(f"Contenedor '{container_name}' NO existe.")
        #     container_client.create_container()
        #     print(f"Contenedor '{container_name}' creado.")
        # else:
        #     print(f"Contenedor '{container_name}' YA existe.")
        # Crear cliente para el blob
        blob_client = container_client.get_blob_client(blob_name)
        
        # Subir el archivo
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            print(f"Archivo '{blob_name}' subido correctamente a '{container_name}'.")
        return urlBlob
        
    except Exception as e:
        print('Update Img Azure error',e)
        return None