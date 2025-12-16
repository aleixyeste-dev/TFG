import os
import re

def cargar_fusiones_desde_txt(ruta="relacionescartas.txt"):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encuentra {ruta}")

    fusiones = {}   # 🔴 ESTA LÍNEA ES LA CLAVE

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()

            if not linea or linea.startswith("#"):
                continue

            izquierda, derecha = linea.split(":")
            
            # Extraer ID del paquete (robusto)
            match = re.search(r"\d+", izquierda)
            if not match:
                raise ValueError(f"No se pudo extraer ID de paquete desde: '{izquierda}'")

            paquete_id = int(match.group())

            actividades = [a.strip() for a in derecha.split(",")]

            fusiones[paquete_id] = actividades

    return fusiones
