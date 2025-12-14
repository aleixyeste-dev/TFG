import os
import random
import re

# ==============================
# Utilidades
# ==============================

def natural_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]


def normalizar_estado(estado):
    """Asegura que el estado tiene siempre la estructura mínima correcta"""
    estado.setdefault("ronda", 1)
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {1: [], 2: []})
    estado.setdefault("proyectos", None)
    estado.setdefault("finalizado", False)
    return estado


# ==============================
# Inicialización
# ==============================

def inicializar_juego():
    return {
        "ronda": 1,
        "historial": [],
        "mazos": {1: [], 2: []},
        "proyectos": None,
        "finalizado": False,
    }


# ==============================
# Carga de estructura de ficheros
# ==============================

def cargar_estructura_proyecto(base_path=None):
    """
    Construye una estructura de proyectos a partir del árbol de carpetas
    imagenes/Proyectos/<id>/Entregables/<ent>/Paquete trabajo/Actividades/*.jpg
    """
    if base_path is None:
        base_path = os.path.join(os.path.dirname(__file__), "imagenes", "Proyectos")

    estructura = {}

    for pid in sorted(os.listdir(base_path), key=natural_key):
        ruta_proyecto = os.path.join(base_path, pid)
        if not os.path.isdir(ruta_proyecto):
            continue

        estructura[pid] = {"actividades": []}

        entregables_path = os.path.join(ruta_proyecto, "Entregables")
        if not os.path.isdir(entregables_path):
            continue

        for eid in sorted(os.listdir(entregables_path), key=natural_key):
            act_path = os.path.join(
                entregables_path, eid, "Paquete trabajo", "Actividades"
            )
            if not os.path.isdir(act_path):
                continue

            for f in sorted(os.listdir(act_path), key=natural_key):
                if f.lower().endswith((".jpg", ".png")):
                    estructura[pid]["actividades"].append(os.path.join(act_path, f))

    return estructura


# ==============================
# Agrupaciones (para fusiones)
# ==============================

def generar_diccionario_agrupaciones(estructura):
    """
    Estructura mínima para permitir fusiones futuras.
    Se deja preparada pero NO bloquea el juego si está vacía.
    """
    return {
        "actividades_a_paquete": {},
        "paquetes_a_entregable": {},
        "entregables_a_proyecto": {},
    }


# ==============================
# Fusión de cartas (SAFE)
# ==============================

def fusionar_cartas(mazo, agrupaciones):
    """
    Intenta fusionar cartas del mazo según las agrupaciones.
    Nunca rompe el estado ni lanza KeyError.
    """
    eventos = []

    if not agrupaciones:
        return mazo, eventos

    actividades_a_paquete = agrupaciones.get("actividades_a_paquete", {})
    paquetes_a_entregable = agrupaciones.get("paquetes_a_entregable", {})
    entregables_a_proyecto = agrupaciones.get("entregables_a_proyecto", {})

    # 🔹 ACTIVIDADES → PAQUETE
    for key, info in actividades_a_paquete.items():
        actividades = info.get("actividades", [])
        carta_resultado = info.get("carta")

        if carta_resultado and all(a in mazo for a in actividades):
            for a in actividades:
                mazo.remove(a)
            mazo.append(carta_resultado)
            eventos.append(f"Fusión completada → {carta_resultado}")

    # 🔹 PAQUETES → ENTREGABLE
    for key, info in paquetes_a_entregable.items():
        paquetes = info.get("paquetes", [])
        carta_resultado = info.get("carta")

        if carta_resultado and all(p in mazo for p in paquetes):
            for p in paquetes:
                mazo.remove(p)
            mazo.append(carta_resultado)
            eventos.append(f"Fusión completada → {carta_resultado}")

    # 🔹 ENTREGABLES → PROYECTO
    for pid, info in entregables_a_proyecto.items():
        entregables = info.get("entregables", [])
        carta_resultado = info.get("carta")

        if carta_resultado and all(e in mazo for e in entregables):
            for e in entregables:
                mazo.remove(e)
            mazo.append(carta_resultado)
            eventos.append(f"Proyecto completado → {carta_resultado}")

    return mazo, eventos


# ==============================
# Lógica de ronda
# ==============================

def siguiente_ronda(estado, estructura, agrupaciones):
    estado = estado.copy()
    eventos = []

    # Incrementar ronda
    estado["ronda"] += 1

    # Asegurar claves
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {"1": [], "2": []})

    for equipo, proyecto in estado["proyectos"].items():
        equipo = str(equipo)

        # Actividades disponibles para ese proyecto
        disponibles = [
            info["carta"]
            for key, info in agrupaciones["actividades_a_paquete"].items()
            if key.startswith(f"{proyecto}_") and info["carta"] not in estado["historial"]
        ]

        if not disponibles:
            continue

        robadas = random.sample(disponibles, min(4, len(disponibles)))

        estado["mazos"][equipo].extend(robadas)
        estado["historial"].extend(robadas)

        eventos.append(
            f"Equipo {equipo} roba {len(robadas)} actividades"
        )

    return estado, eventos
