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

def cargar_estructura_proyecto(base_path=None):
    if base_path is None:
        base_path = os.path.join(os.path.dirname(__file__), "imagenes", "Proyectos")

    estructura = {}

    for pid in sorted(os.listdir(base_path), key=natural_key):
        ruta = os.path.join(base_path, pid)
        if not os.path.isdir(ruta):
            continue

        estructura[pid] = {"actividades": []}

        entregables = os.path.join(ruta, "Entregables")
        if not os.path.isdir(entregables):
            continue

        for eid in sorted(os.listdir(entregables), key=natural_key):
            act_path = os.path.join(
                entregables, eid, "Paquete trabajo", "Actividades"
            )
            if not os.path.isdir(act_path):
                continue

            for f in sorted(os.listdir(act_path), key=natural_key):
                if f.lower().endswith((".jpg", ".png")):
                    estructura[pid]["actividades"].append(
                        os.path.join(act_path, f)
                    )

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

