import os
import re

def cargar_fusiones_desde_txt(ruta="relacionescartas.txt"):
    """
    Lee el archivo relacionescartas.txt con formato:
    Paquete 15 --> 47,48,49,50

    Devuelve:
    {
        15: {47, 48, 49, 50},
        16: {51, 52, 53, 54},
        ...
    }
    """
    fusiones = {}

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encuentra {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or "-->" not in linea:
                continue

            izquierda, derecha = linea.split("-->")
            match = re.search(r"\d+", izquierda)
            if not match:
                raise ValueError(f"No se pudo extraer ID de paquete desde: '{izquierda}'")

                paquete_id = int(match.group())

            actividades = {
                int(x.strip()) for x in derecha.split(",")
            }

            fusiones[paquete_id] = actividades

    return fusiones


# Se carga UNA VEZ al importar
FUSIONES_PAQUETES = cargar_fusiones_desde_txt()
