# fusiones.py
import os

RUTA_TXT = "relacionescartas.txt"


def cargar_fusiones_desde_txt():
    ruta = RUTA_TXT

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encuentra {ruta}")

    fusiones = {}

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()

            # Saltar líneas vacías o comentarios
            if not linea or linea.startswith("#"):
                continue

            # 👇 ESTA ES LA LÍNEA CLAVE CORREGIDA
            izquierda, derecha = linea.split(":", 1)

            paquete_id = int(
                izquierda.replace("Paquete", "").strip()
            )

            actividades = [
                int(x.strip()) for x in derecha.split(",")
            ]

            fusiones[paquete_id] = actividades

    return fusiones


# Se carga UNA VEZ al importar el módulo
FUSIONES_PAQUETES = cargar_fusiones_desde_txt()
