# fusiones.py
import os

RUTA_TXT = "relacionescartas.txt"

def cargar_fusiones_desde_txt():
    fusiones = {}

    if not os.path.exists(RUTA_TXT):
        raise FileNotFoundError(f"No se encuentra {RUTA_TXT}")

    with open(RUTA_TXT, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            izquierda, derecha = linea.split(":", 1)

            paquete_id = int(
                izquierda.replace("Paquete", "").strip()
            )

            actividades = [
                int(x.strip()) for x in derecha.split(",")
            ]

            fusiones[paquete_id] = actividades

    return fusiones


FUSIONES_PAQUETES = cargar_fusiones_desde_txt()

