import os
import random
import re

# ==============================
# Utilidades
# ==============================

def natural_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]


def normalizar_estado(estado):
    estado.setdefault("ronda", 0)
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {"1": [], "2": []})
    estado.setdefault("proyectos", {})
    estado.setdefault("finalizado", False)
    return estado


# ==============================
# Inicialización
# ==============================

def inicializar_juego():
    return {
        "ronda": 0,
        "historial": [],
        "mazos": {"1": [], "2": []},
        "proyectos": {},
        "finalizado": False,
    }


# ==============================
# Carga estructura
# ==============================

def cargar_estructura_proyecto():
    base_path = "/mount/src/tfg/imagenes/Proyectos"

    if not os.path.exists(base_path):
        raise RuntimeError(f"No existe la ruta {base_path}")

    estructura = {}
    for pid in sorted(os.listdir(base_path)):
        ruta_proyecto = os.path.join(base_path, pid)
        if not os.path.isdir(ruta_proyecto):
            continue

        actividades = []
        ruta_actividades = os.path.join(
            ruta_proyecto, "Entregables", "Paquete trabajo", "Actividades"
        )

        if os.path.exists(ruta_actividades):
            for f in os.listdir(ruta_actividades):
                if f.lower().endswith(".jpg"):
                    actividades.append(os.path.join(ruta_actividades, f))

        estructura[pid] = {
            "actividades": actividades
        }

    return estructura



# ==============================
# Agrupaciones (placeholder)
# ==============================

def generar_diccionario_agrupaciones(estructura):
    return {
        "actividades_a_paquete": {},
        "paquetes_a_entregable": {},
        "entregables_a_proyecto": {},
    }


# ==============================
# Fusión SAFE
# ==============================

def fusionar_cartas(mazo, agrupaciones):
    eventos = []
    fusiones = fusiones_disponibles(mazo, agrupaciones)

    if not fusiones:
        return mazo, eventos

    # Ejecutar SOLO una fusión por ronda
    fusion = fusiones[0]

    for carta in fusion["cartas"]:
        mazo.remove(carta)

    carta_fusionada = fusion["resultado"]
    mazo.append(carta_fusionada)

    eventos.append(
        f"Fusión realizada: {len(fusion['cartas'])} cartas → paquete"
    )

    return mazo, eventos



# ==============================
# Ronda
# ==============================

def siguiente_ronda(estado, estructura, agrupaciones):
    estado = normalizar_estado(estado.copy())
    eventos = []

    # Asignar proyectos si no existen
    if not estado["proyectos"]:
        proyectos = list(estructura.keys())
        estado["proyectos"] = {
            "1": random.choice(proyectos),
            "2": random.choice(proyectos),
        }

    estado["ronda"] += 1

    for equipo, proyecto in estado["proyectos"].items():
        actividades = estructura.get(proyecto, {}).get("actividades", [])

        disponibles = [a for a in actividades if a not in estado["historial"]]
        if not disponibles:
            disponibles = actividades.copy()

        if disponibles:
            robadas = random.sample(disponibles, min(4, len(disponibles)))
            estado["mazos"][equipo].extend(robadas)
            estado["historial"].extend(robadas)
            eventos.append(f"Equipo {equipo} roba {len(robadas)} cartas")

    return estado, eventos



import os

import fusiones

FUSIONES_PAQUETES = fusiones.FUSIONES_PAQUETES


def obtener_id_carta(ruta):
    """
    Extrae el ID numérico de una carta desde la ruta de la imagen
    """
    return int(ruta.split("/")[-1].replace(".jpg", ""))


def fusiones_disponibles(mazo):
    """
    Devuelve una lista de paquetes que pueden fusionarse con el mazo actual
    """
    ids_mazo = {obtener_id_carta(c) for c in mazo}
    disponibles = []

    for paquete_id, actividades in FUSIONES_PAQUETES.items():
        if actividades.issubset(ids_mazo):
            disponibles.append({
                "paquete": paquete_id,
                "actividades": actividades
            })

    return disponibles

import os


def ruta_paquete(paquete_id):
    """
    Construye la ruta de la imagen del paquete de trabajo
    Ajusta la ruta si tus imágenes están en otra carpeta
    """
    return f"/mount/src/tfg/imagenes/Paquetes/{paquete_id}.jpg"


def aplicar_fusion(estado, equipo, paquete_id):
    """
    Aplica una fusión:
    - Elimina las actividades del paquete
    - Añade la carta del paquete
    """
    mazo = estado["mazos"][str(equipo)]
    actividades = FUSIONES_PAQUETES[paquete_id]

    nuevo_mazo = []
    for carta in mazo:
        if obtener_id_carta(carta) not in actividades:
            nuevo_mazo.append(carta)

    nuevo_mazo.append(ruta_paquete(paquete_id))
    estado["mazos"][str(equipo)] = nuevo_mazo

    return estado

