# fusiones.py
import os

def cargar_fusiones_desde_txt():
    """
    Devuelve un dict:
    {
        15: [47,48,49,50],
        16: [51,52,53,54],
        ...
    }
    """
    fusiones = {}

    ruta = os.path.join(os.path.dirname(__file__), "relacionescartas.txt")

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encuentra el archivo: {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue

            # Ejemplo línea:
            # Paquete 15: 47,48,49,50
            izquierda, derecha = linea.split(":")
            paquete_id = int(izquierda.replace("Paquete", "").strip())

            actividades = [
                int(x.strip()) for x in derecha.split(",")
            ]

            fusiones[paquete_id] = actividades

    return fusiones


# ✅ ESTA LÍNEA ES CLAVE
FUSIONES_PAQUETES = cargar_fusiones_desde_txt()
