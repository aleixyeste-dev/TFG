# entregables.py
from pathlib import Path

def cargar_entregables_desde_txt(ruta="relacionesentregables.txt"):
    entregables = {}
    ruta = Path(ruta)

    if not ruta.exists():
        return entregables

    with ruta.open(encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or ":" not in linea:
                continue

            izquierda, derecha = linea.split(":", 1)
            entregable_id = int(izquierda.replace("Entregable", "").strip())
            paquetes = {int(x.strip()) for x in derecha.split(",")}

            entregables[entregable_id] = paquetes

    return entregables


ENTREGABLES = cargar_entregables_desde_txt()
