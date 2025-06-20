# src/flask_api/routes.py
from flask import Flask, jsonify, render_template_string,request,render_template,flash,redirect, url_for
from invias.src.app.ingesta.updateImg import updateImgElastic,validarImages,validar_calidad
from invias.src.app.ingesta.validarFaltantes import validarFaltantesLocalmente
from invias.src.app.ingesta.cleanElastic import cleanElasticImg
from invias.src.app.ingesta.General import restaurar
import json
import os
import io
import sys

#from requests import request
from rest_framework import status
from threading import Thread

flask_app = Flask(__name__)


flask_app.secret_key = 'saroa'


Home = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Software de Calidad - INVIAS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

    <div class="container py-5">
        <div class="text-center mb-5">
            <h1 class="display-4 text-primary">Software de Calidad - INVIAS</h1>
            <p class="lead">Herramienta de validación y control de calidad de Ingesta Conteos Moviles</p>
        </div>

        <div class="row justify-content-center">
            <!-- Validar Imágenes -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Gestion De Imágenes</h5>
                            <a href="/validar-imgs-form" class="btn btn-primary w-100">Iniciar</a>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Validar Calidad -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Hoja de vida</h5>
                            <a href="/validar-calidad-form" class="btn btn-primary w-100">Iniciar</a>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Validar registros faltantes -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Gestion Registros Faltantes</h5>
                            <a href="/validar-registros-form" class="btn btn-primary w-100">Iniciar</a>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Gestion Duplicidad</h5>
                            <a href="/validar-duplicidad" class="btn btn-primary w-100">Iniciar</a>
                        </form>
                    </div>
                </div>
            </div>
            <!-- General -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Proceso Ingesta</h5>
                            <a href="/General-form" class="btn btn-primary w-100">Iniciar</a>
                            <a href="/procesos" class="btn btn-outline-secondary mt-3">Ver Procesos</a>
                        </form>
                    </div>
                </div>
            </div>


        </div>
    </div>
    {% with messages = get_flashed_messages() %}
  {% if messages %}
    <div class="alert alert-info" role="alert">
      {% for message in messages %}
        {{ message }}
      {% endfor %}
    </div>
  {% endif %}
{% endwith %}


</body>
</html>
"""

form_calidad= """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Calidad - Hoja De Vida</title>
</head>
<body class="bg-light" >

    <div class="container py-5">
        <a href="/" style="width:50px;height:40px;padding: 5px 5px;;"class="btn btn-danger">Atras</a>
        
        <div class="row justify-content-center">
            
            

            <!-- Validar Calidad -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center" >Hoja De Vida x Dispositivo</h5>
                        <form method="post" action="/validar-calidad-form">
                            <div class="mb-3">
                                <label for="device" class="form-label">Dispositivo</label>
                                <input type="text" class="form-control" name="device" required>
                            </div>
                            <div class="mb-3">
                                <label for="path" class="form-label">Ruta</label>
                                <input type="text" class="form-control" name="path" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Iniciar</button>
                        </form>
                    </div>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""


form_gestionar_imgs= """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Gestion de Imágenes</title>
</head>
<body class="bg-light">

    <div class="container py-5">
        <a href="/" style="width:50px;height:40px;padding: 5px 5px;;"class="btn btn-danger">Atras</a>
        
        <div class="row justify-content-center">
            

            <!-- Validar imagenes -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" >Gestion De Imagenes Faltantes</h5>
                        <form method="post" action="/validar-imagenes-form">
                            <div class="mb-3">
                                <label for="device" class="form-label">Dispositivo</label>
                                <input type="text" class="form-control" name="device" required>
                            </div>
                            <div class="mb-3">
                                <label for="path" class="form-label">Ruta</label>
                                <input type="text" class="form-control" name="path" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Iniciar</button>
                        </form>
                    </div>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""


form_regis_faltantes= """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Gestion de Registros faltantes</title>
</head>
<body class="bg-light">

    <div class="container py-5">
        <a href="/" style="width:50px;height:40px;padding: 5px 5px;;"class="btn btn-danger">Atras</a>
        
        <div class="row justify-content-center">
            

            <!-- Validar imagenes -->
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" >Gestion de Registros Faltantes</h5>
                        <form method="post" action="/validar-registros-form">
                            <div class="mb-3">
                                <label for="device" class="form-label">Dispositivo</label>
                                <input type="text" class="form-control" name="device" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Iniciar</button>
                        </form>
                    </div>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""

form_dplicados= """

<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Gestion de Duplicidad</title>
</head>
<body class="bg-light">

    <div class="container py-5">
        <a href="/" style="width:50px;height:40px;padding: 5px 5px;;"class="btn btn-danger">Atras</a>
        
        <div class="row justify-content-center">
            
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" >Gestion de Duplicidad</h5>
                        <form method="post" action="/validar-duplicidad">
                            <div class="mb-3">
                                <label for="device" class="form-label">Dispositivo</label>
                                <input type="text" class="form-control" name="device" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Iniciar</button>
                        </form>
                    </div>
                </div>
            </div>

        </div>
    </div>

</body>
</html>
"""


form_General= """
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Proceso General de ingesta</title>
</head>
<body class="bg-light" >

    <div class="container py-5">
        <a href="/" style="width:50px;height:40px;padding: 5px 5px;" class="btn btn-danger">Atras</a>

        <div class="row justify-content-center">
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title" style="text-align:center">Proceso Ingesta</h5>
                        <form id="generalForm" method="post" action="/General-form">
                            <div class="mb-3">
                                <label for="device" class="form-label">Dispositivo</label>
                                <input type="text" class="form-control" name="device" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="device" class="form-label">URL Backup</label>
                                <input type="text" class="form-control" name="url" required>
                            </div>
                        
                            <div class="mb-3">
                                <label for="path" class="form-label">Ruta Imagenes</label>
                                <input type="text" class="form-control" name="path" required>
                            </div>
                            <div class="mb-3">
                                <label for="kafka_env" class="form-label">Entorno Kafka</label>
                                <select class="form-select" name="kafka_env" required>
                                    <option value="" disabled selected>Seleccione una opción</option>
                                    <option value="QA">QA</option>
                                    <option value="PROD">PROD</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Iniciar</button>
                        </form>
                        <div id="loadingBar" class="progress mt-3" style="display:none;">
    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width:100%">Procesando...</div>
</div>
<script>
document.getElementById('generalForm').addEventListener('submit', function() {
    document.getElementById('loadingBar').style.display = 'block';
});
</script>
                    </div>
                </div>
            </div>
        </div>
    </div>

</body>
</html>
"""






@flask_app.route('/procesos')
def mostrar_procesos():
    log_path = "procesos_log.txt"  # archivo donde guardarás temporalmente la traza
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
    else:
        contenido = "❌ No se ha generado ningún proceso aún."

    return render_template('procesos.html', log=contenido)



@flask_app.route("/")
def index():
    return render_template_string(Home)

@flask_app.route("/validar-calidad-form")
def calidad():
    return render_template_string(form_calidad)

@flask_app.route("/validar-imgs-form")
def gestionar_imgs():
    return render_template_string(form_gestionar_imgs)

@flask_app.route("/validar-registros-form")
def gestionar_registros():
    return render_template_string(form_regis_faltantes)

@flask_app.route("/validar-duplicidad")
def gestionar_duplicidad():
    return render_template_string(form_dplicados)

@flask_app.route("/General-form")
def General():
    return render_template_string(form_General)










@flask_app.route("/validar-imgs-form", methods=["POST"])
def validar_imagenes_form():
    device = request.form.get("device")
    path = request.form.get("path")
    try:
        validarImages(device, path)
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px;'>
        ✅ <strong>Validación de imágenes completada</strong> para <strong>{device}</strong>.
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""

    except Exception as e:
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #D8000C; background-color: #FFD2D2; padding: 10px; border-radius: 5px;'>
        ❌ <strong>Error:</strong> {str(e)}
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""

    


@flask_app.route("/validar-calidad-form", methods=["POST"])
def validar_calidad_form():
    device = request.form.get("device")
    path = request.form.get("path")
    response = {'status': True}
    status_response = status.HTTP_200_OK
    pathNew = path.replace('/', '\\')

    try:
        
        Thread(target=validar_calidad, args=(device, pathNew)).start()
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #333;'>
        ✅ La verificación de calidad para <strong>{device}</strong> se está ejecutando en segundo plano.
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""

    except Exception as e:
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #D8000C; background-color: #FFD2D2; padding: 10px; border-radius: 5px;'>
        ❌ <strong>Error:</strong> {str(e)}
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""

    


@flask_app.route("/validar-registros-form", methods=["POST"])
def validar_registros_form():
    response = {'status': True}
    status_response = status.HTTP_200_OK
    device = request.form.get("device")

    urlElastic = 'http://20.99.184.101/elastic-api/'
    try:
        
        Thread(target=validarFaltantesLocalmente,
           args=(urlElastic, device)).start()
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #333;'>
        ✅ La verificación de faltantes para <strong>{device}</strong> se está ejecutando en segundo plano.
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""
    except Exception as e:
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #D8000C; background-color: #FFD2D2; padding: 10px; border-radius: 5px;'>
        ❌ <strong>Error:</strong> {str(e)}
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""
    


@flask_app.route("/validar-duplicidad", methods=["POST"])
def validar_duplicados_form():
    response = {'status': True}
    status_response = status.HTTP_200_OK
    device = request.form.get("device")

    urlElastic = 'http://20.99.184.101/elastic-api/'
    try:
        
        Thread(target=cleanElasticImg,
           args=(urlElastic, device)).start()
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #333;'>
        ✅ La verificación de Duplicados para <strong>{device}</strong> se está ejecutando en segundo plano.
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""
    except Exception as e:
        return f"""
<div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
    <p style='font-size: 18px; color: #D8000C; background-color: #FFD2D2; padding: 10px; border-radius: 5px;'>
        ❌ <strong>Error:</strong> {str(e)}
    </p>
    <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;'>
        Volver
    </a>
</div>
"""


    
@flask_app.route("/General-form", methods=["POST"])
def General_form():
    import io, sys
    from flask import request, redirect, url_for, flash
    from threading import Thread

    url = request.form.get("url")
    device = request.form.get("device")
    path = request.form.get("path")
    entorno_kafka = request.form.get("kafka_env")

    try:
        path = path.replace('/', '\\')
        url = url.replace('/', '\\')

        # Capturar salida del proceso
        buffer = io.StringIO()
        sys.stdout = buffer

        # Ejecutar proceso en hilo
        Thread(target=restaurar, args=(device, url, path, entorno_kafka)).start()

        sys.stdout = sys.__stdout__  # restaurar consola
        log_output = buffer.getvalue()

        # Guardar traza en archivo
        with open("procesos_log.txt", "w", encoding='utf-8') as f:
            f.write(log_output)

        flash("✅ Proceso en segundo plano iniciado.")
        return redirect(url_for('index'))

    except Exception as e:
        sys.stdout = sys.__stdout__
        with open("procesos_log.txt", "w", encoding='utf-8') as f:
            f.write(f"❌ Error: {str(e)}")

        return f"""
        <div style='font-family: Arial, sans-serif; padding: 20px; text-align: center;'>
            <p style='font-size: 18px; color: #D8000C; background-color: #FFD2D2; padding: 10px; border-radius: 5px;'>
                ❌ <strong>Error:</strong> {str(e)}
            </p>
            <a href='/' style='display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 4px;'>
                Volver
            </a>
        </div>
        """


























if __name__ == "__main__":
    flask_app.run(debug=True)

