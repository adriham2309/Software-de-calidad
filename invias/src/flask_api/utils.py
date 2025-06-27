procesos_en_cola = []

def agregar_proceso(nombre, estado="En proceso"):
    procesos_en_cola.append({"nombre": nombre, "estado": estado, "progreso": 0})

def actualizar_progreso(nombre, progreso):
    for p in procesos_en_cola:
        if p["nombre"] == nombre:
            p["progreso"] = progreso
            
def actualizar_estado_y_progreso(nombre, nuevo_estado, nuevo_progreso):
    for p in procesos_en_cola:
        if p["nombre"] == nombre:
            p["estado"] = nuevo_estado
            p["progreso"] = nuevo_progreso
            