
def getDataJson(key, key3):
    json_1 = getJson_1()
    json_2 = getJson_2()
    json_3 = getJson_3()
    if key in json_1:
        return json_1[key]
    elif key in json_2:
        return json_2[key]
    elif key3 in json_3:
        return json_3[key3]
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
        "AUTOMOVIL-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 3
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
        "CAMIONETA-3-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "CAMIONETA-4-CA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "MOTOCARRO-0-2": {
            "TPDCategory": "C2",
            "invias.id": 7,
            "invias.class": "QUAD",
            "TPDCategory.id": 4,
            "inviasCustom.id": 7
        },
        "MOTOCARRO-2-2": {
            "TPDCategory": "C2",
            "invias.id": 7,
            "invias.class": "QUAD",
            "TPDCategory.id": 4,
            "inviasCustom.id": 7
        },
        "MOTOCARRO-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 7,
            "invias.class": "QUAD",
            "TPDCategory.id": 2,
            "inviasCustom.id": 7
        },
        "BUS-2-2": {
            "TPDCategory": "C2",
            "invias.id": 5,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 4,
            "inviasCustom.id": 5
        },
        "BUS-0-2": {
            "TPDCategory": "C2",
            "invias.id": 5,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 4,
            "inviasCustom.id": 5
        },
        "BUS-3-2": {
            "TPDCategory": "C2",
            "invias.id": 5,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 4,
            "inviasCustom.id": 5
        },
        "BUS-2-3": {
            "TPDCategory": "C3",
            "invias.id": 5,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 5,
            "inviasCustom.id": 5
        },
        "MOTOCICLETA-0-2": {
            "TPDCategory": "C2",
            "invias.id": 8,
            "invias.class": "QUAD",
            "TPDCategory.id": 4,
            "inviasCustom.id": 8
        },
        "TRACTOCAMION-3-3S3": {
            "TPDCategory": "C6",
            "invias.id": 54,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 8,
            "inviasCustom.id": 54
        },
        "TRACTOCAMION-2-3S3": {
            "TPDCategory": "C6",
            "invias.id": 54,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 8,
            "inviasCustom.id": 54
        },
        "TRACTOCAMION-0-3S3": {
            "TPDCategory": "C6",
            "invias.id": 54,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 8,
            "inviasCustom.id": 54
        },
        "TRACTOCAMION-0-3S3": {
            "TPDCategory": "TRACTOCAMION",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 15,
            "inviasCustom.id": 0
        },
        "TRACTOCAMION-3-3S2": {
            "TPDCategory": "C5",
            "invias.id": 55,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 55
        },
        "TRACTOCAMION-2-3S2": {
            "TPDCategory": "C5",
            "invias.id": 55,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 55
        },
        "TRACTOCAMION-0-3S2": {
            "TPDCategory": "C5",
            "invias.id": 55,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 55
        },
        "TRACTOCAMION-2-2S3": {
            "TPDCategory": "C5",
            "invias.id": 57,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 57
        },
        "TRACTOCAMION-3-2S3": {
            "TPDCategory": "C5",
            "invias.id": 57,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 57
        },
        "TRACTOCAMION-0-2S3": {
            "TPDCategory": "C5",
            "invias.id": 57,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 3 ejes",
            "TPDCategory.id": 7,
            "inviasCustom.id": 57
        },
        "TRACTOCAMION-2-2S2": {
            "TPDCategory": "C4",
            "invias.id": 58,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 58
        },
        "TRACTOCAMION-3-2S2": {
            "TPDCategory": "C4",
            "invias.id": 58,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 58
        },
        "TRACTOCAMION-4-2S2": {
            "TPDCategory": "C4",
            "invias.id": 58,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 58
        },
        "TRACTOCAMION-3-3S1": {
            "TPDCategory": "C4",
            "invias.id": 56,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 1 eje",
            "TPDCategory.id": 6,
            "inviasCustom.id": 56
        },
        "TRACTOCAMION-3-3S4": {
            "TPDCategory": "C7",
            "invias.id": 60,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de más de 3 ejes",
            "TPDCategory.id": 9,
            "inviasCustom.id": 60
        },
        "TRACTOCAMION-3-3S2S2": {
            "TPDCategory": "C7",
            "invias.id": 30,
            "invias.class": "Tractocamión de 3 ejes-Semiremolque de 2 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 9,
            "inviasCustom.id": 30
        },
        "CAMION-2-2": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "CAMION-0-2": {
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
        "CAMION-2-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "CAMION-0-2": {
            "TPDCategory": "CAMION",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 13,
            "inviasCustom.id": 0
        },
        "CAMION-0-3": {
            "TPDCategory": "CAMION",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 13,
            "inviasCustom.id": 0
        },
        "CAMION-0-4": {
            "TPDCategory": "CAMION",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 13,
            "inviasCustom.id": 0
        },
        "CAMION-3-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "CAMION-2-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "CAMION-0-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "CAMION-4-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "CAMION-2-2B1": {
            "TPDCategory": "C3",
            "invias.id": 42,
            "invias.class": "Camión Rígido de 2 ejes-Remolque Balanceado de 1 eje",
            "TPDCategory.id": 5,
            "inviasCustom.id": 42
        },
        "CAMION-2-V3": {
            "TPDCategory": "C3",
            "invias.id": 21,
            "invias.class": "Volqueta de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 21
        },
        "CAMION-0-V3": {
            "TPDCategory": "C3",
            "invias.id": 21,
            "invias.class": "Volqueta de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 21
        },
        "CAMION-2-2S1": {
            "TPDCategory": "C3",
            "invias.id": 59,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 1 eje",
            "TPDCategory.id": 5,
            "inviasCustom.id": 59
        },
        "CAMION-2-2R2": {
            "TPDCategory": "C4",
            "invias.id": 46,
            "invias.class": "Camión Rígido de 2 ejes-Remolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 46
        },
        "CAMION-0-2R2": {
            "TPDCategory": "C4",
            "invias.id": 46,
            "invias.class": "Camión Rígido de 2 ejes-Remolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 46
        },
        "CAMION-4-4": {
            "TPDCategory": "C4",
            "invias.id": 34,
            "invias.class": "Camión Rígido de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 34
        },
        "CAMION-2-4": {
            "TPDCategory": "C4",
            "invias.id": 34,
            "invias.class": "Camión Rígido de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 34
        },
        "CAMION-3-4": {
            "TPDCategory": "C4",
            "invias.id": 34,
            "invias.class": "Camión Rígido de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 34
        },
        "CAMION-0-4": {
            "TPDCategory": "C4",
            "invias.id": 34,
            "invias.class": "Camión Rígido de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 34
        },
        "CAMION-2-2B2": {
            "TPDCategory": "C4",
            "invias.id": 41,
            "invias.class": "Camión Rígido de 2 ejes-Remolque Balanceado de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 41
        },
        "CAMION-2-2S2": {
            "TPDCategory": "C4",
            "invias.id": 58,
            "invias.class": "Tractocamión de 2 ejes-Semiremolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 58
        },
        "CAMION-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "CAMION-0-CA": {
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
        "VOLQUETA-2-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "VOLQUETA-0-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "VOLQUETA-3-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "VOLQUETA-4-V2": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "VOLQUETA-2-2": {
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
        "VOLQUETA-3-V3": {
            "TPDCategory": "C3",
            "invias.id": 21,
            "invias.class": "Volqueta de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 21
        },
        "VOLQUETA-0-V3": {
            "TPDCategory": "C3",
            "invias.id": 21,
            "invias.class": "Volqueta de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 21
        },
        "VOLQUETA-2-V3": {
            "TPDCategory": "C3",
            "invias.id": 21,
            "invias.class": "Volqueta de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 21
        },
        "VOLQUETA-3-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "VOLQUETA-0-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "VOLQUETA-2-3": {
            "TPDCategory": "C3",
            "invias.id": 35,
            "invias.class": "Camión Rígido de 3 ejes",
            "TPDCategory.id": 5,
            "inviasCustom.id": 35
        },
        "VOLQUETA-0-V2": {
            "TPDCategory": "VOLQUETA",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 14,
            "inviasCustom.id": 0
        },
        "VOLQUETA-0-V3": {
            "TPDCategory": "VOLQUETA",
            "invias.id": 0,
            "invias.class": "undefined",
            "TPDCategory.id": 14,
            "inviasCustom.id": 0
        },
        "VOLQUETA-4-V4": {
            "TPDCategory": "C4",
            "invias.id": 40,
            "invias.class": "Volqueta de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 40
        },
        "VOLQUETA-2-V4": {
            "TPDCategory": "C4",
            "invias.id": 40,
            "invias.class": "Volqueta de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 40
        },
        "VOLQUETA-4-4": {
            "TPDCategory": "C4",
            "invias.id": 34,
            "invias.class": "Camión Rígido de 4 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 34
        },
        "VOLQUETA-2-V2R2": {
            "TPDCategory": "C4",
            "invias.id": 17,
            "invias.class": "Volqueta de 2 ejes-Remolque de 2 ejes",
            "TPDCategory.id": 6,
            "inviasCustom.id": 17
        },
        "VOLQUETA-0-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "VOLQUETA-3-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        },
        "VOLQUETA-2-CA": {
            "TPDCategory": "Autos",
            "invias.id": 23,
            "invias.class": "Camioneta de 2 ejes",
            "TPDCategory.id": 2,
            "inviasCustom.id": 23
        }
    }
    
def getJson_2():
    return {}

def getJson_3():
    return {
        "CAMIONETA": {
            "TPDCategory": "Autos",
            "invias.id": 1,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 1
        },
        "CAMPERO": {
            "TPDCategory": "Autos",
            "invias.id": 2,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 2
        },
        "AUTOMOVIL": {
            "TPDCategory": "Autos",
            "invias.id": 3,
            "invias.class": "(A) Automóvil, campero, pick-ups, camioneta y microbús",
            "TPDCategory.id": 2,
            "inviasCustom.id": 3
        },
        "MICROBUS": {
            "TPDCategory": "Buses",
            "invias.id": 4,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 3,
            "inviasCustom.id": 4
        },
        "BUS": {
            "TPDCategory": "Buses",
            "invias.id": 5,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 3,
            "inviasCustom.id": 5
        },
        "BUSETA": {
            "TPDCategory": "Buses",
            "invias.id": 6,
            "invias.class": "(B) Bus y buseta",
            "TPDCategory.id": 3,
            "inviasCustom.id": 6
        },
        "MOTOCARRO": {
            "TPDCategory": "Motocicleta",
            "invias.id": 7,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 7
        },
        "MOTOCICLETA": {
            "TPDCategory": "Motocicleta",
            "invias.id": 8,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 8
        },
        "MOTOTRICICLO": {
            "TPDCategory": "Motocicleta",
            "invias.id": 9,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 9
        },
        "TRICIMOTO": {
            "TPDCategory": "Motocicleta",
            "invias.id": 10,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 10
        },
        "CICLOMOTOR": {
            "TPDCategory": "Motocicleta",
            "invias.id": 11,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 11
        },
        "CUADRICICLO": {
            "TPDCategory": "Motocicleta",
            "invias.id": 12,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 12
        },
        "CUATRIMOTO": {
            "TPDCategory": "Motocicleta",
            "invias.id": 13,
            "invias.class": "QUAD",
            "TPDCategory.id": 1,
            "inviasCustom.id": 13
        },
        "SIN CLASE": {
            "TPDCategory": "undefined",
            "invias.id": 14,
            "invias.class": "QUAD",
            "TPDCategory.id": 0,
            "inviasCustom.id": 14
        },
        "VOLQUETA": {
            "TPDCategory": "C2",
            "invias.id": 22,
            "invias.class": "Volqueta de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 22
        },
        "CAMION": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
        "TRACTOCAMION": {
            "TPDCategory": "C2",
            "invias.id": 36,
            "invias.class": "Camión Rígido de 2 ejes",
            "TPDCategory.id": 4,
            "inviasCustom.id": 36
        },
    }