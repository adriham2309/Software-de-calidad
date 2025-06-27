from requests.auth import HTTPBasicAuth 
import json
import requests
from django.conf import settings
import pyodbc 
import os.path
from invias.src.app.ingesta.updateImgAzure import updateImgAzure
import os
from datetime import datetime, timedelta
import subprocess
from invias.src.flask_api.utils import agregar_proceso,actualizar_progreso,procesos_en_cola, actualizar_estado_y_progreso
import time




def updateImgElastic(urlElastic, device, path, database,proceso_img):
    size_num = 10000
    run_state = True

    search_after = None
    total_elements = 0
    noEncontradas = 0
    while run_state:
        json_data = query(size_num, device)

        if search_after:
            json_data["search_after"] = search_after

        data_query = json.dumps(json_data)

        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json'}

        obj_response = requests.post(
            urlElastic+'neural.plates.output*/_search?format=json',
            auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASS),
            data=data_query,
            headers=headers
        )

        try:
            elementos = json.loads(obj_response.text)
            if len(elementos['hits']['hits']) == 0:
                actualizar_progreso(proceso_img, 100)
                run_state = False
                print('----- Finished:', device,' -----')
            else:
                try:
                    # Crear conexion
                    connection = conexionDBLocal(device, database)
                    cursor = connection.cursor()
                    for item in elementos['hits']['hits']:

                        # Ejecutar una consulta de prueba
                        # print('item', item)
                        incidence_id = item["_source"]['attributes']['incidence_id']
                        number_plate = item["_source"]['payload']['plate']
                        # print('incidence_id', incidence_id)
                        # print('number_plate', number_plate)
                        cursor.execute(
                            "SELECT ai.INCIDENCEID, ai.ImageSource, ai.CutImageSource FROM RESULTS r INNER JOIN ANPR_Images ai on r.INCIDENCEID = ai.INCIDENCEID WHERE r.INCIDENCEID = ? AND r.NumberPlate = ?", (incidence_id, number_plate))
                        actualizar_estado_y_progreso(proceso_img, "Consultando Imagenes Encontradas Y No Encontradas",55)
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        results = [dict(zip(columns, row)) for row in rows]
                        loadImageFull = None
                        loadImagePlate = None
                        for result in results:
                            imageSource = result['ImageSource']
                            cutImageSource = result['CutImageSource']
                            if 'c:' in imageSource:
                                imageSource = imageSource.replace('c:', path)
                            elif 'C:' in imageSource:
                                imageSource = imageSource.replace('C:', path)
                            if 'c:' in cutImageSource:
                                cutImageSource = cutImageSource.replace(
                                    'c:', path)
                            elif 'C:' in cutImageSource:
                                cutImageSource = cutImageSource.replace(
                                    'C:', path)
                            # print('ImageSource',result['ImageSource'])
                            # print('CutImageSource',result['CutImageSource'])
                            if os.path.exists(imageSource):
                                loadImageFull = updateImgAzure(
                                    imageSource, incidence_id)
                            else:
                                noEncontradas += 1
                                logTxt(device+'_NO_ENCONTRADAS',
                                       str(result['INCIDENCEID'])+', '+imageSource)
                            if os.path.exists(cutImageSource):
                                loadImagePlate = updateImgAzure(
                                    cutImageSource, incidence_id)
                            else:
                                noEncontradas += 1
                                logTxt(
                                    device+'_NO_ENCONTRADAS', str(result['INCIDENCEID'])+', '+cutImageSource)
                            actualizar_estado_y_progreso(proceso_img, "Actualizando Campos Con Imagenes Encontradas",60)
                            if loadImageFull and loadImagePlate:
                                data_update = {
                                    "doc": {
                                        "payload": {
                                            "img_path": loadImageFull,
                                            "img_path_plate": loadImagePlate
                                        },
                                        "attributes": {
                                            "avi_file_name": loadImageFull
                                        }
                                    }
                                }
                                actualizar_estado_y_progreso(proceso_img, "Campos De Imagenes Encontradas Actualizados",75)

                                url_update_index = item["_index"] + \
                                    "/_update/" + item["_id"]
                                data_query_update = json.dumps(data_update)
                                headers = {'Accept': 'application/json',
                                           'Content-type': 'application/json'}
                                update_response = requests.post(
                                    urlElastic + url_update_index,
                                    auth=HTTPBasicAuth(
                                        settings.ELASTIC_USER, settings.ELASTIC_PASS),
                                    data=data_query_update,
                                    headers=headers
                                )
                                actualizar_estado_y_progreso(proceso_img, "Actualizando Indices",85)

                                update_response_text = json.loads(
                                    update_response.text)
                                print('update_response_text:',
                                      update_response_text)
                                actualizar_estado_y_progreso(proceso_img, "Actualizando",95)


                        # print('----------------------------------------------------')
                    last_item = elementos['hits']['hits'][-1]
                    search_after = last_item['sort']
                    actualizar_estado_y_progreso(proceso_img, "Actualizacion realizada",100)

                except Exception as e:
                    print("Error al conectar a la base de datos:", e)

                finally:
                    # Cerrar la conexion
                    if 'connection' in locals() and connection is not None:
                        connection.close()

                total_elements += len(elementos['hits']['hits'])
                print(device, '=>', total_elements)

        except Exception as e:
            print('While error:::::::::::::::::::::::::::::')
            print(e)


def query(size_num, device):
    return {
        "from": 0,
        "size": size_num,
        "sort": [
            {
                "@timestamp": {
                    "order": "asc"
                }
            },
            "_score"
        ],
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "catalog.desc": device
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "boost": 2,
                                "format": "yyyy-MM-dd HH:mm:ss.SSSZZ",
                                "gte": "2024-01-01 00:00:00.000-0500",
                                "lte": "2024-12-31 23:59:59.999-0500"
                            }
                        }
                    }
                ],
                "must_not": {
                    "exists": {
                        "field": "payload.img_path"
                    }
                }
            }
        }
    }


def validarImages(device, path,proceso_img):

    try:

        database = 'ANPR'+device
        connection = conexionDBLocal(device, database)
        cursor = connection.cursor()

        # cursor.execute("SELECT * FROM ANPR_Images")
        cursor.execute(
            "SELECT r.INCIDENCEID, ai.ImageSource, ai.CutImageSource FROM RESULTS r INNER JOIN ANPR_Images ai on r.INCIDENCEID = ai.INCIDENCEID")
        actualizar_estado_y_progreso(proceso_img, "Consultando Imagenes En La BD",35)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        count = 0
        countExist = 0
        countExistProcessed = 0
        countNotExist = 0
        for result in results:
            count += 1
            imageSource = result['ImageSource']
            if 'c:' in imageSource:
                imageSource = imageSource.replace('c:', path)
            elif 'C:' in imageSource:
                imageSource = imageSource.replace('C:', path)

            cutImageSource = result['CutImageSource']
            if 'c:' in cutImageSource:
                cutImageSource = cutImageSource.replace('c:', path)
            elif 'C:' in cutImageSource:
                cutImageSource = cutImageSource.replace('C:', path)
            notExistImg = ''
            existImgProcessed = ''
            if not os.path.exists(imageSource):
                if os.path.exists(imageSource+'.processed'):
                    existImgProcessed = str(
                        result['INCIDENCEID'])+', ' + imageSource+'.processed'
                    countExistProcessed += 1
                    print(count, 'EXIST IMG PROCESSED',
                          '->', imageSource+'.processed')
                else:
                    notExistImg = str(result['INCIDENCEID'])+', ' + imageSource
                    countNotExist += 1
                    print(count, 'NOT EXIST IMG', '->', imageSource)
            else:
                countExist += 1
                print(count, 'EXIST IMG', '->', imageSource)

            if not os.path.exists(cutImageSource):
                if os.path.exists(cutImageSource+'.processed'):
                    countExistProcessed += 1
                    print(count, 'EXIST IMG PROCESSED',
                          '->', imageSource+'.processed')
                    if existImgProcessed == '':
                        existImgProcessed = str(
                            result['INCIDENCEID'])+', ' + cutImageSource+'.processed'
                    else:
                        existImgProcessed = existImgProcessed+', '+cutImageSource+'.processed'
                else:
                    if notExistImg == '':
                        notExistImg = str(
                            result['INCIDENCEID'])+', ' + cutImageSource
                    else:
                        notExistImg = notExistImg+', '+cutImageSource
                    countNotExist += 1
                    print(count, 'NOT EXIST IMG', '->', cutImageSource)
            else:
                countExist += 1
                print(count, 'EXIST IMG', '->', cutImageSource)

            if notExistImg != '':
                logTxt(device+'_NOT_EXIST', notExistImg)

            if existImgProcessed != '':
                logTxt(device+'_PROCESSED', existImgProcessed)

        logTxt(device+'_resumen', 'Total: '+str(count)+', Sin subir: '+str(countExist) +
               ', Subidas: '+str(countExistProcessed)+', No Existen: '+str(countNotExist))
        print(' --> FINISHED <-- ')
        actualizar_estado_y_progreso(proceso_img, "Consultando Imagenes Existentes O No Existentes",45)
        # Subir imagenes faltantes
        if countExist > 0:
            print(' --> Inicia proceso de subir imagenes faltantes <-- ')
            urlElastic = 'http://20.99.184.101/elastic-api/'
            updateImgElastic(urlElastic, device, path, database,proceso_img)

    except Exception as e:
        print("Error al conectar a la base de datos:", e)


def validar_calidad(device, path,proceso_HV):
    
    nombre_proceso = f"Proceso General Ingesta: {device}"
    actualizar_estado_y_progreso(nombre_proceso, "Hoja De Vida En Proceso", 25)
    actualizar_estado_y_progreso(proceso_HV, "En Proceso", 20)
    
    
    #Primer parte total de imagenes 
    print(device)
     # Define extensiones de imagenes que quieres contar
    ext_img = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    ext_img_1 = ('.processed')
    ext_img_2 = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp','.processed')
    
    # Ruta raiz donde estan las carpetas de los dispositivos
    ruta_carpeta = path

    # Inicializa el contador
    total_img = 0
    total_img1 = total_img
    total_img2 = 0
    total_img_dividido=0
    
    # Recorre las carpetas y subcarpetas
    for ruta, carpetas, archivos in os.walk(ruta_carpeta):
        # Filtra los archivos que sean imagenes
        total_img += sum(1 for archivo in archivos if archivo.lower().endswith(ext_img))

    for ruta, carpetas, archivos in os.walk(ruta_carpeta):
        # Filtra los archivos que sean imagenes
        total_img1 += sum(1 for archivo in archivos if archivo.lower().endswith(ext_img_1))

    for ruta, carpetas, archivos in os.walk(ruta_carpeta):
        # Filtra los archivos que sean imagenes
        total_img2 += sum(1 for archivo in archivos if archivo.lower().endswith(ext_img_2))

    logTxt1(device,
    "=================================================",
    "",
    f"Dispositivo: {device}",
    f"ruta: {ruta_carpeta}",
    f"Total de imagenes sin cargar: {total_img}",
    f"Total Dividido: {total_img / 2}",
    f"Total imagenes Procesadas: {total_img1}",
    f"Total Dividido: {total_img1 / 2}",
    "====================================",
    f"Total Imagenes: {total_img2}"
    )

    print("=================================================")
    print()
    print(f"ruta: ",ruta_carpeta)
    print(f"Total de imagenes sin cargar: {total_img}")
    print(f"Total Dividido: {total_img / 2}")
    print(f"Total imagenes Procesadas: {total_img1}")
    print(f"Total Dividido: {total_img1/2}")
    print()
    print("=================================================")
    print(f"Total Imgagenes: {total_img2}")
    print("=================================================")
    actualizar_estado_y_progreso(proceso_HV, "Informacion Sobre la carpeta de imagenes", 30)

    try:
        #segunda parte  match de imagenes con registros 
        # Conectar a la base de datos
        database = 'ANPR' + device
        connection = conexionDBLocal(device, database)
        cursor = connection.cursor()
        
        #Querys necesarias hoja de vida 
        
        #computerid,velocidad-1,no_plate
        # Ejecutar la primera consulta para obtener computerid
        query2 = "SELECT computerid FROM results GROUP BY computerid"
        cursor.execute(query2)
        fila2 = cursor.fetchone()
        valor_columna4 = fila2[0] if fila2 else 0

        # Ejecutar la segunda consulta para contar velocidades -1
        query3 = "SELECT COUNT(speed) AS total_velocidad FROM results WHERE speed = '-1'"
        cursor.execute(query3)
        fila3 = cursor.fetchone()
        valor_columna5 = fila3[0] if fila3 else 0

        # Ejecutar la tercera consulta para contar placas nulas
        query4 = "SELECT COUNT(NumberPlate) AS Total_placas FROM results WHERE NumberPlate IS NULL"
        cursor.execute(query4)
        fila4 = cursor.fetchone()
        valor_columna6 = fila4[0] if fila4 else 0
        
        #total results
        query5 = "SELECT COUNT(*)AS Total FROM results"
        cursor.execute(query5)
        fila5 = cursor.fetchone()
        valor_columna7 = fila5[0] if fila5 else 0
        
        #total results
        query6 = "SELECT COUNT(*)AS Total FROM anpr_images"
        cursor.execute(query6)
        fila6 = cursor.fetchone()
        valor_columna8 = fila6[0] if fila6 else 0
        
        

        resultado1 = " -->computer ID: " + str(valor_columna4)
        resultado2 = " -->Velocidad -1: " + str(valor_columna5)
        resultado3 = " -->NO_PLATE: " + str(valor_columna6)
        resultado5 = str(valor_columna7)
        resultado6 = str(valor_columna8)
        print(resultado1, resultado2, resultado3)
        logTxt1(device, resultado1 + "\n" + resultado2 + "\n" + resultado3)
        logTxt1(device,"\n"*1)
        
        
        #  rutas de las imagenes desde la base de datosx registro
        cursor.execute('SELECT incidenceid,ImagePath, CutImageSource FROM ANPR_Images')
        registros = cursor.fetchall()
        directorio = path
        actualizar_estado_y_progreso(proceso_HV, "Hoja De Vida En Proceso -- Informacion BD", 40)
        actualizar_estado_y_progreso(nombre_proceso, "Hoja De Vida En Proceso -- Informacion BD", 25)
        # Obtener todos los nombres de archivos de imagenes en el directorio y sus subcarpetas
        nombres_img = set()
        for root, _, files in os.walk(directorio):
            for file in files:
                nombres_img.add(file.lower().strip())

        #  Verificar cantidad de imagenes en la carpeta y ejemplos
        print(f"Total de imagenes en '{directorio}' y subcarpetas: {len(nombres_img)}")
        print("Ejemplo de nombres encontrados:", list(nombres_img)[:5])

        # Contador para seguimiento del progreso
        contador = 0
        total_registros = len(registros)

        logTxt1(device,"=================================================")
        logTxt1(device,"---Inicia el proceso de Validacion de imagenes---")
        logTxt1(device,"=================================================")

        # Validar si ambas imagenes existen por cada registro en la BD
        contar1 = 0
        contar2 = 0
        for incidenceid, ruta1, ruta2 in registros:
            nombre_imagen1 = os.path.basename(ruta1).strip().lower()
            nombre_imagen2 = os.path.basename(ruta2).strip().lower()

            # Incrementar contador y mostrar progreso
            contador += 1
            print(f"Procesando {contador}/{total_registros}: {nombre_imagen1}, {nombre_imagen2}")

            existe_img1 = nombre_imagen1 in nombres_img
            existe_img2 = nombre_imagen2 in nombres_img

            if existe_img1 and existe_img2:
                logTxt4(device, f'IncidenceID {incidenceid}   --Si esta relacionado a imagenes.')
                contar1 += 1
            else:
                mensaje_error = f'IncidenceID {incidenceid} --NO esta relacionado a: '
                if not existe_img1 and not existe_img2:
                    mensaje_error += "ninguna de las dos imagenes."
                elif not existe_img1:
                    mensaje_error += f"la imagen 1 ({nombre_imagen1})."
                elif not existe_img2:
                    mensaje_error += f"la imagen 2 ({nombre_imagen2})."

                logTxt2(device, mensaje_error)
                contar2 += 1
        uso=contar1*2
        # Mensaje de finalizacion
        logTxt1(device,
                f"Proceso finalizado. Total de registros procesados: {contador}/{total_registros}", "\n",
                f"--> Total de registros con  imagen relacionada : {contar1} <--", "\n",
                f"--> Total de registros que la imagen no esta relacionada: {contar2} <--", "\n",

                f"--> Total de imagenes en uso: {uso} <--", "\n",
                f"--> Total de imagenes sobrantes: {total_img - uso} <--", "\n",
                "================================================================", "\n")
        logTxt1(device, "--> Validacion de registros VS imagenes finalizada <--")
        print("--> Validacion de imagenes finalizada <--")
        actualizar_estado_y_progreso(proceso_HV, "Validacion Imagenes Finalizada", 50)
        actualizar_estado_y_progreso(nombre_proceso, "Validacion Imagenes Finalizada", 25)
        #duplicados 
        query5 = '''
            SELECT DISTINCT incidenceid, numberplate, timestamp 
            FROM RESULTS 
            WHERE EXISTS (
            SELECT 1 
            FROM RESULTS AS sub 
            WHERE sub.incidenceid = RESULTS.incidenceid 
            AND sub.numberplate = RESULTS.numberplate 
            AND sub.timestamp = RESULTS.timestamp 
            GROUP BY sub.incidenceid, sub.numberplate, sub.timestamp 
            HAVING COUNT(*) > 1
            );
        '''
        cursor.execute(query5)
        fila5 = cursor.fetchall()
        logTxt1(device,"=====================================")
        logTxt1(device,"---Inicia el proceso de duplicados---")
        logTxt1(device,"=====================================","\n"*1)
        duplicados1 = 0
        
        for i in fila5:
           
            resultado4 = f"IncidenceID: {i[0]}"
            
            
            if resultado4==0:
                resultado4='Sin registros duplicados'
                duplicados1 = duplicados1 + 1
                logTxt1(device,"Registros Duplicados: ",duplicados1,"\n"*1)
            else:
                duplicados1 = duplicados1 + 1
                logTxt1(device,f'Total de duplicados: {duplicados1}')
                duplicados='Los registros son: '
        
            logTxt3(device,duplicados+resultado4)
            logTxt1(device,"Registros Duplicados: ",duplicados1,"\n"*1)
            logTxt1(device,"=======================================")
            logTxt1(device,"---Finaliza el proceso de Duplicados---")
            logTxt1(device,"=======================================")
            logTxt1(device,"\n"*1)
        logTxt1(device,f"Registros Duplicados: "+str(duplicados1),"\n"*1)
        actualizar_estado_y_progreso(proceso_HV, "Validacion Duplicados En BD Finalizada", 60)
        actualizar_estado_y_progreso(nombre_proceso, "Validacion Duplicados En BD Finalizada", 25)
        #rango de fecha 
        query = 'select MIN(TimeStamp)as Fecha_Inicial, max(TimeStamp)as Fecha_ultima from RESULTS'
        cursor.execute(query)
        fila = cursor.fetchone()
        if fila:
        
            valor_columna1 = fila[0]  
            valor_columna2 = fila[1]  
    
        
            resultado =" -->fecha Inicial: " +str(valor_columna1) +"   "+"-->fecha final: " + str(valor_columna2)
            print(resultado)
        else:
            print("No se encontraron registros")
        logTxt1(device,"=======================================")
        logTxt1(device, f"Rango de fecha:",resultado)
        actualizar_estado_y_progreso(proceso_HV, "Validacion Rango De Fechas Finalizada", 70)
        actualizar_estado_y_progreso(nombre_proceso, "Validacion Rango De Fechas Finalizada", 25)
        #fechas
        query0 = 'SELECT DISTINCT CAST(timestamp AS DATE) AS fecha FROM results ORDER BY fecha;'
        cursor.execute(query0)
        filas0 = cursor.fetchall()
        dias=0

        if filas0:
            logTxt1(device, "=======================================")
            for fila in filas0:
                valor_columna1 = fila[0]  
                resultado = f"--> Fecha: {valor_columna1}"
                dias=dias + 1
                print(resultado)
                logTxt1(device, resultado)  
        else:
            print(device, "No se encontraron fechas en la base de datos.")

        logTxt1(device, "=======================================")  
        actualizar_estado_y_progreso(proceso_HV, "Validacion Dias Entre Fechas Finalizada", 80)
        actualizar_estado_y_progreso(nombre_proceso, "Validacion Dias Entre Fechas Finalizada", 25)

        #dias entre fecha
        logTxt1(device,f'-->Total de dias entre fechas: {dias}')
        
        #fechas consecutivas
        query00 = 'SELECT DISTINCT CAST(timestamp AS DATE) AS fecha FROM results ORDER BY fecha;'
        cursor.execute(query00)
        filas00 = cursor.fetchall()  # Obtener todas las filas

        if filas00:
            logTxt1(device, "=======================================")
            fechas = [fila[0] for fila in filas00]
            
            
            # Verificar si las fechas son consecutivas
            son_consecutivas = True
            consecutivas=""
            for i in range(len(fechas) - 1):
                diferencia = (fechas[i + 1] - fechas[i]).days

                if diferencia != 1:
                    son_consecutivas = False
                    logTxt1(device, f"Ruptura encontrada: {fechas[i]} y {fechas[i + 1]} no son consecutivas.")
                    
    
            if son_consecutivas:
                consecutivas="SI"
                logTxt1(device, "Los dias son consecutivos: SI ")
                print("las fechas son consecutivas.")
            else:
                consecutivas= "NO"
                logTxt1(device, "Los dias son consecutivos: NO ")
                print("las fechas no son consecutivas.")
        else:
            logTxt1(device, "No se encontraron fechas en la base de datos.")
            print("No se encontraron fechas en la base de datos.")

        logTxt1(device, "=======================================","\n"*2)
        logTxt1(device, "=============Resumen=============")
        logTxt1(device,f"""
--> Registros con imagenes imcompletas: {contar2}
{resultado2}
--> Total Registros Tabla Results: {resultado5}
--> Total Registros Tabla Anpr_images: {resultado6}
--> Total de dias: {dias}
--> Dias Conecutivos: {consecutivas}
        """)
        actualizar_estado_y_progreso(proceso_HV, "Validacion Dias Consecutivos Finalizada", 90)
        actualizar_estado_y_progreso(nombre_proceso, "Validacion Dias Consecutivos Finalizada", 25)

        
        print('\n'*1)
        print('--> Fin del proceso: Dispositivo ',device,'<--')
        print('\n'*1)
        
        actualizar_estado_y_progreso(proceso_HV, "Proceso Hoja De Vida Finalizado", 100)
        actualizar_estado_y_progreso(nombre_proceso, "Proceso Hoja De Vida Finalizado", 35)

        insert_sql = """
    update ingesta.dbo.Procesos set Estado=6 where Dispositivo=?;
    """
        cursor.execute(insert_sql, (device))
        print("✅ Registro de proceso insertado.")
        
        
        
        consulta_sql = """
    select estado from ingesta.dbo.Procesos  where Dispositivo=? and Estado=6;
    """
        cursor.execute(consulta_sql, (device))
        existe=cursor.fetchone
        
        if existe:
            exe_file = 'C:\\Ingesta_Invias_V-Prod_1.2\\Invias.NL.Relay.exe'
            urlhost='http://0.0.0.0:8000'
            ejecutar(exe_file,urlhost,device)

        else:
                print("--> No se completó alguno de los procesos de restauración.")
                
        cursor.close()
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        
        
        
        
def ejecutar(exe_file, urlhost, device):
    import time
    nombre_proceso = f"Proceso General Ingesta: {device}"
    actualizar_estado_y_progreso(nombre_proceso, "Inicia Ejecucion", 45)

    try:
        server = '(localdb)\\aplicacion'
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server};"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        if not os.path.exists(exe_file):
            print(f"❌ No se encontró el ejecutable: {exe_file}")
            return
        
        working_dir = os.path.dirname(exe_file)

        # Ejecutar el .exe con la URL 
        subprocess.Popen([exe_file, urlhost], shell=True, cwd=working_dir)
        actualizar_estado_y_progreso(nombre_proceso, "Inicia Proceso De Ingesta", 50)


        insert_sql = """
    update ingesta.dbo.Procesos set Estado=7 where Dispositivo=?;
    """
        cursor.execute(insert_sql, (device))
        print("✅ Registro de proceso insertado.")

        print(f"✅ Ejecutado correctamente: {exe_file} con argumento {urlhost}")
        
        txt_log_path = f"C:\\tmp\\Logs\\{device}.txt"  # Ahora busca un .txt

        # Bucle infinito hasta encontrar el mensaje en el log
        while True:
            try:
                if os.path.exists(txt_log_path):
                    with open(txt_log_path, "r", encoding="utf-8") as f:
                        contenido = f.read()
                        if "[INF] NO events found to load" in contenido:
                            actualizar_estado_y_progreso(nombre_proceso, "✅ Proceso De Ingesta Finalizado", 100)
                            print("✅ Progreso actualizado a 100% Ingesta finalizada.")
                            break
            except Exception as e:
                print(f"❌ Error al leer el log TXT: {e}")
            time.sleep(180)  # Espera 3 minutos antes de volver a intentar

    except Exception as e:
        print(f"❌ Error al ejecutar el archivo: {e}")
        
    





#Funcion para crear los logs de la aplicacion
def logTxt(name, text):
    fileInfo = open(name+".txt", "a+")
    fileInfo.write(text + "\n")
    fileInfo.close()
#log general   
def logTxt1(name, *lines):
    with open(name+".txt", "a+") as fileInfo:
        for line in lines:
            fileInfo.write(line + "\n")

#log sin imagenes relacionadas            
def logTxt2(name, *lines):
    with open(name+"_no_relacionadas.txt", "a+") as fileInfo:
        for line in lines:
            fileInfo.write(line + "\n")
            
#log general imagenes relacionadas            
def logTxt4(name, *lines):
    with open(name+"relacionadas.txt", "a+") as fileInfo:
        for line in lines:
            fileInfo.write(line + "\n")

#log duplicados           
def logTxt3(name, *lines):
    with open(name+"Duplicados.txt", "a+") as fileInfo:
        for line in lines:
            fileInfo.write(line + "\n")
            



def conexionDBLocal(device, database):
    # Configuracion de conexion
    # server = 'localhost' # Para MAC
    server = '(localdb)\\aplicacion'  # Para Windows
    username = ''
    password = ''
    # Crear conexion para MAC
    # connection = pyodbc.connect(
    #     "DRIVER={ODBC Driver 18 for SQL Server};"
    #     f"SERVER={server};"
    #     f"DATABASE={database};"
    #     f"UID={username};"
    #     f"PWD={password};"
    #     "TrustServerCertificate=yes;"
    # )
    # Crear conexion para Windows
    connection = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "TrustServerCertificate=yes;"
    )
    print(" -- Conexion exitosa DB Local -- ")
    return connection
