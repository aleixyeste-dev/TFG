import os
import random
import re

# ===============================
# CONFIGURACIÓN
# ===============================

BASE_PATH = os.path.join(os.path.dirname(__file__), "imagenes", "Proyectos")

EMPAREJAMIENTOS = {
    "1": "2", "2": "1",
    "3": "4", "4": "3",
    "5": "6", "6": "5"
}

# ===============================
# UTILIDADES
# ===============================

def natural_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]


def normalizar_estado(estado):
    # Asegurar estructura básica
    if "mazos" not in estado or not isinstance(estado["mazos"], dict):
        estado["mazos"] = {}

    mazos_norm = {}
    for k, v in estado["mazos"].items():
        try:
            mazos_norm[int(k)] = v
        except:
            pass

    estado["mazos"] = mazos_norm

    # Garantizar que existen los dos equipos
    estado["mazos"].setdefault(1, [])
    estado["mazos"].setdefault(2, [])

    return estado


# ===============================
# CARGA DE ESTRUCTURA
# ===============================

def cargar_estructura_proyecto():
    estructura = {}

    for proyecto_id in sorted(os.listdir(BASE_PATH), key=natural_key):
        ruta_proyecto = os.path.join(BASE_PATH, proyecto_id)
        if not os.path.isdir(ruta_proyecto):
            continue

        estructura[proyecto_id] = {"actividades": []}

        for root, _, files in os.walk(ruta_proyecto):
            for f in files:
                if f.lower().endswith(".jpg"):
                    estructura[proyecto_id]["actividades"].append(os.path.join(root, f))

    return estructura


# ===============================
# INICIALIZACIÓN
# ===============================

def inicializar_juego():
    return {
        "ronda": 1,
        "historial": [],
        "mazos": {
            1: [],
            2: []
        },
        "proyectos": None,
        "finalizado": False
    }

# ===============================
# LÓGICA DE RONDAS
# ===============================

def siguiente_ronda(estado, estructura, agrupaciones=None):
    estado = normalizar_estado(estado)
    eventos = []

    proyectos_disponibles = list(estructura.keys())

    # Asignación de proyectos en la primera ronda
    if estado["ronda"] == 1:
        p1 = random.choice(proyectos_disponibles)
        p2 = EMPAREJAMIENTOS.get(p1, random.choice(proyectos_disponibles))
        estado["proyectos"] = {1: p1, 2: p2}
        eventos.append(f"Proyecto equipo 1: {p1}")
        eventos.append(f"Proyecto equipo 2: {p2}")

    # Reparto de actividades
    for equipo, proyecto in estado["proyectos"].items():
        disponibles = [
            a for a in estructura[proyecto]["actividades"]
            if a not in estado["historial"]
        ]

        if disponibles:
            robadas = random.sample(disponibles, min(16, len(disponibles)))
            estado["historial"].extend(robadas)
            estado["mazos"].setdefault(equipo, [])
            estado["mazos"][equipo].extend(robadas)
            eventos.append(f"Equipo {equipo} roba {len(robadas)} actividades")

    estado["ronda"] += 1
    return estado, eventos
