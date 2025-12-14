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

def fusionar_cartas(mazo, agrupaciones=None):
    """
    Versión segura: por ahora NO elimina cartas ni rompe el flujo.
    Devuelve el mazo tal cual y una lista de eventos.
    """
    eventos = []

    # Si no hay reglas de fusión, no hacer nada
    if not agrupaciones:
        return mazo, eventos

    # Punto de extensión futuro (TFG)
    return mazo, eventos


# ==============================
# Lógica de ronda
# ==============================

def siguiente_ronda(estado, estructura, agrupaciones=None):
    estado = normalizar_estado(dict(estado))
    eventos = []

    # Asignación inicial de proyectos
    if estado["proyectos"] is None:
        proyectos = list(estructura.keys())
        if len(proyectos) < 2:
            estado["finalizado"] = True
            return estado, eventos

        p1 = random.choice(proyectos)
        p2 = random.choice([p for p in proyectos if p != p1])
        estado["proyectos"] = {1: p1, 2: p2}
        eventos.append(f"Proyecto equipo 1: {p1}")
        eventos.append(f"Proyecto equipo 2: {p2}")

    # Reparto de actividades
    for equipo, proyecto in estado["proyectos"].items():
        actividades = estructura.get(proyecto, {}).get("actividades", [])

        disponibles = [
            a for a in actividades
            if a not in estado["historial"]
        ]

        # Si no quedan nuevas, permitir repetir
        if not disponibles:
            disponibles = list(actividades)

        if disponibles:
            robadas = random.sample(disponibles, min(16, len(disponibles)))
            estado["historial"].extend(robadas)
            estado["mazos"][equipo].extend(robadas)

    # Fusión (no destructiva)
    for equipo in (1, 2):
        mazo, nuevos_eventos = fusionar_cartas(
            estado["mazos"][equipo], agrupaciones
        )
        estado["mazos"][equipo] = mazo
        eventos.extend(nuevos_eventos)

    estado["ronda"] += 1
    return estado, eventos
