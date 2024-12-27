"""
URL configuration for invias project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from invias import views
from invias.src.connection import one
from invias.src.app.ingesta import app, clean

urlpatterns = [
    path('start/<str:option>', views.start),
    path('start_process', views.start_process),
    path('group_data_test', views.group_data_test),
    path('load/<str:option>', views.load),
    path('test/<str:option>/<int:start>/<int:end>', views.load_multi_text),
    path('state_error/<str:option>', views.state_error),
    path('detail_method/<str:option>', views.detail_method),
    path('open_log/<str:option>', views.open_log),
    path('elastic', one.elastic),
    path('load_data/<str:option>', one.load_data),
    path('ingesta/update_data', app.updateData),
    path('ingesta/update_runt/<str:start>/<str:end>', app.updateRunt),
    path('ingesta/clean_data/<str:device>', clean.cleanData),
    path('ingesta/pasar_data/<str:device>', clean.pasarData),
    path('ingesta/update_img/<str:device>', app.updateImg),
    path('ingesta/validate_img/<str:device>/<str:path>', app.validateImg),
    path('ingesta/validar_faltantes/<str:device>', app.validarFaltantes),
]
