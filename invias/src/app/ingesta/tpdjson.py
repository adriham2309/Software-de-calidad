
def getDataJson(key):
    json_1 = getJson_1()
    json_2 = getJson_2()
    if key in json_1:
        return json_1[key]
    elif key in json_2:
        return json_2[key]
    else:
        return {}
    
def getJson_1():
    return {
        "AUTOMOVIL-0-2": {
            "TPDCategory": "C2",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 4,
            "inviasCustom.id": 3
        },
        "CAMION-0-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "MICROBUS-0-2": {
            "TPDCategory": "C2",
            "invias.id": 4,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 4,
            "inviasCustom.id": 4
        },
        "AUTOMOVIL-2-2": {
            "TPDCategory": "C2",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 4,
            "inviasCustom.id": 3
        },
        "CAMION-2-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "MICROBUS-2-2": {
            "TPDCategory": "C2",
            "invias.id": 4,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 4,
            "inviasCustom.id": 4
        },
        "MICROBUS-2-Buses": {
            "TPDCategory": "Buses",
            "invias.id": 4,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 3,
            "inviasCustom.id": 4
        },
        "VOLQUETA-2-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "CAMION-3-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "TRACTOCAMION-3-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "VOLQUETA-3-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "CAMION-4-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "CAMION-6-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "TRACTOCAMION-2-2S": {
            "TPDCategory": "C2",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 4,
            "inviasCustom.id": 0
        },
        "AUTOMOVIL-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 3
        },
        "CAMION-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMIONETA-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "CAMPERO-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 2,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 2
        },
        "VOLQUETA-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMIONETA-1-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "AUTOMOVIL-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 3
        },
        "CAMION-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMIONETA-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "CAMPERO-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 2,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 2
        },
        "VOLQUETA-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMION-3-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMIONETA-3-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "VOLQUETA-3-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMIONETA-4-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "VOLQUETA-0-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 23
        },
        "CAMION-2-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 23
        },
        "VOLQUETA-2-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 23
        },
        "VOLQUETA-3-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 23
        },
        "VOLQUETA-4-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 23
        }
    }
    
def getJson_2():
    return {
        "MOTOCARRO-2": {
            "TPDCategory": "C2",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 4,
            "inviasCustom.id": 3
        }
    }