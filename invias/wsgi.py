# src/wsgi.py

import os
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Importa tu app Flask
from src.flask_api.routes import flask_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invias.settings')

django_app = get_wsgi_application()

# se Usa DispatcherMiddleware para unir Flask a Django
application = DispatcherMiddleware(django_app, {
    '/flask': flask_app,  # Todo lo que comience con /flask/ se va a Flask
})
