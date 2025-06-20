@echo off
:: Verifica si se está ejecutando como admin, si no, relanza como admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

cd /d "C:\Users\adriham\Documents\Work\Desarrollo\endpoint_calidad\calidad_del_dato1.2"
call env\Scripts\activate
waitress-serve --host=0.0.0.0 --port=5000 invias.src.flask_api.routes:flask_app
