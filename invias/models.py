from django.db import models
from datetime import datetime

class Method_Publication(models.Model):
    name = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    modify_date = models.DateTimeField(auto_now=True)
    last_process = models.DateTimeField(null=True)
    verification_date = models.DateTimeField(null=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
def pending_directory_path(instance):
    date = str(datetime.now().strftime("%d%m%Y")) + "/"
    name = date + str(datetime.now().strftime("%H%M%S-%f")) + ".json"
    return 'pendind/{0}/{1}'.format(instance.method_publication.name, name)
    
class Pending(models.Model):
    """
        status:
        0 - Creado
        1 - En Proceso
        2 - Enviado Correctamente.
        3 - Falla - Servicios MinT.
        4 - Falla - UT
    """
    method_publication = models.ForeignKey(Method_Publication, on_delete=models.CASCADE)
    path = models.FileField(upload_to=pending_directory_path, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return self.status
    
def store_directory_path(instance):
    date = str(datetime.now().strftime("%d%m%Y")) + "/"
    name = date + str(datetime.now().strftime("%H%M%S-%f")) + ".json"
    return 'store/{0}/{1}'.format(instance.pending.method_publication.name, name)
    
class Store(models.Model):
    """
        status:
        0 - Creado
        1 - En Proceso
        2 - Enviado Correctamente.
        3 - Error.
        4 - Falla - Servicios MinT.
        5 - Falla - UT.
    """
    pending = models.ForeignKey(Pending, on_delete=models.CASCADE)
    error_description = models.TextField()
    path = models.FileField(upload_to=store_directory_path, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return self.status

class Device(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SiteReferenceDevice(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    version = models.IntegerField(default=0)
    json_data = models.TextField()
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.version
